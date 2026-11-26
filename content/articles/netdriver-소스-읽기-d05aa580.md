---
title: "NetDriver 소스 읽기"
category: content/categories/topic-07-03.json
order: 20
---
---

<details>
<summary>원문</summary>

```c++
/**
 *****************************************************************************************
 * NetDrivers, NetConnections, and Channels
 *****************************************************************************************
 *
 *
 * UNetDrivers are responsible for managing sets of UNetConnections, and data that can be shared between them.
 * There is typically a relatively small number of UNetDrivers for a given game. These may include:
 *	- The Game NetDriver, responsible for standard game network traffic.
 *	- The Demo NetDriver, responsible for recording or playing back previously recorded game data. This is how Replays work.
 *	- The Beacon NetDriver, responsible for network traffic that falls outside of "normal" gameplay traffic.
 *
 * Custom NetDrivers can also be implemented by games or applications and used.
 * NetConnections represent individual clients that are connected to a game (or more generally, to a NetDriver).
 *
 * End point data isn't directly handled by NetConnections. Instead NetConnections will route data to Channels.
 * Every NetConnection will have its own set of channels.
 *
 * Common types of channels:
 *
 *	- A Control Channel is used to send information regarding state of a connection (whether or not the connection should close, etc.)
 *	- A Voice Channel may be used to send voice data between client and server.
 *	- A Unique Actor Channel will exist for every Actor replicated from the server to the client.
 *
 * Custom Channels can also be created and used for specialized purposes (although, this isn't very common).
 *
 *
 *****************************************************************************************
 * Game Net Drivers, Net Connections, and Channels
 *****************************************************************************************
 *
 *
 * Under normal circumstances, there will exist only a single NetDriver (created on Client and Server) for "standard" game traffic and connections.
 *
 * The Server NetDriver will maintain a list of NetConnections, each representing a player that is in the game. It is responsible for
 * replicating Actor Data.
 *
 * Client NetDrivers will have a single NetConnection representing the connection to the Server.
 *
 * On both Server and Client, the NetDriver is responsible for receiving Packets from the network and passing those to the appropriate
 * NetConnection (and establishing new NetConnections when necessary).
 *
 *
 *****************************************************************************************
 *****************************************************************************************
 *****************************************************************************************
 * Initiating Connections / Handshaking Flow.
 *****************************************************************************************
 *****************************************************************************************
 *****************************************************************************************
 *
 *
 * UIpNetDriver and UIpConnection (or derived classes) are the engine defaults for almost every platform, and everything below
 * describes how they establish and manage connections. These processes can differ between implementations of NetDriver, however.
 *
 * Both Server and Clients will have have their own NetDrivers, and all UE Replicated Game traffic will be sent by or Received
 * from the IpNetDriver. This traffic also includes logic for establishing connections, and re-establishing connections when
 * something goes wrong.
 *
 * Handshaking is split across a couple of different places: NetDriver, PendingNetGame, World, PacketHandlers, and maybe others.
 * The split is due to having separate needs, things such as: determining whether or not an incoming connection is sending data in "UE-Protocol",
 * determining whether or not an address appears to be malicious, whether or not a given client has the correct version of a game, etc.
 *
 *
 *****************************************************************************************
 * Startup and Handshaking
 *****************************************************************************************
 *
 *
 * Whenenever a server Loads a map (via UEngine::LoadMap), we will make a call into UWorld::Listen.
 * That code is responsible for creating the main Game Net Driver, parsing out settings, and calling UNetDriver::InitListen.
 * Ultimately, that code will be responsible for figuring out what how exactly we listen for client connections.
 * For example, in IpNetDriver, that is where we determine the IP / Port we will bind to by calls to our configured Socket Subsystem
 * (see ISocketSubsystem::GetLocalBindAddresses and ISocketSubsystem::BindNextPort).
 *
 * Once the server is listening, it's ready to start accepting client connections.
 *
 * Whenever a client wants to Join a server, they will first establish a new UPendingNetGame in UEngine::Browse with the server's IP.
 * UPendingNetGame::Initialize and UPendingNetGame::InitNetDriver are responsible for initializing settings and setting up the NetDriver respectively.
 * Clients will immediately setup a UNetConnection for the server as a part of this initialization, and will start sending data to the server on that connection,
 * initiating the handshaking process.
 *
 * On both Clients and Server, UNetDriver::TickDispatch is typically responsible for receiving network data.
 * Typically, when we receive a packet, we inspect its address and see whether or not it's from a connection we already know about.
 * We determine whether or not we've established a connection for a given source address by simply keeping a map from FInternetAddr to UNetConnection.
 *
 * If a packet is from a connection that's already established, we pass the packet along to the connection via UNetConnection::ReceivedRawPacket.
 * If a packet is not from a connection that's already established, we treat is as "connectionless" and begin the handshaking process.
 *
 * See StatelessConnectionHandlerComponent.cpp for details on how this handshaking works.
 *
 *
 *****************************************************************************************
 * UWorld / UPendingNetGame / AGameModeBase Startup and Handshaking
 *****************************************************************************************
 *
 *
 * After the UNetDriver and UNetConnection have completed their handshaking process on Client and Server,
 * UPendingNetGame::SendInitialJoin will be called on the Client to kick off game level handshaking.
 *
 * Game Level Handshaking is done through a more structured and involved set of FNetControlMessages.
 * The full set of control messages can be found in DataChannel.h.
 *
 * Most of the work for handling these control messages are done either in UWorld::NotifyControlMessage,
 * and UPendingNetGame::NotifyControlMessage. Briefly, the flow looks like this:
 *
 * Client's UPendingNetGame::SendInitialJoin sends NMT_Hello.
 *
 * Server's UWorld::NotifyControlMessage receives NMT_Hello, sends NMT_Challenge.
 *
 * Client's UPendingNetGame::NotifyControlMessage receives NMT_Challenge, and sends back data in NMT_Login.
 *
 * Server's UWorld::NotifyControlMessage receives NMT_Login, verifies challenge data, and then calls AGameModeBase::PreLogin.
 * If PreLogin doesn't report any errors, Server calls UWorld::WelcomePlayer, which call AGameModeBase::GameWelcomePlayer,
 * and send NMT_Welcome with map information.
 *
 * Client's UPendingNetGame::NotifyControlMessage receives NMT_Welcome, reads the map info (so it can start loading later),
 * and sends an NMT_NetSpeed message with the configured Net Speed of the client.
 *
 * Server's UWorld::NotifyControlMessage receives NMT_NetSpeed, and adjusts the connections Net Speed appropriately.
 *
 * At this point, the handshaking is considered to be complete, and the player is fully connected to the game.
 * Depending on how long it takes to load the map, the client could still receive some non-handshake control messages
 * on UPendingNetGame before control transitions to UWorld.
 *
 * There are also additional steps for handling Encryption when desired.
 *
 *
 *****************************************************************************************
 * Reestablishing Lost Connections
 *****************************************************************************************
 *
 *
 * Throughout the course of a game, it's possible for connections to be lost for a number of reasons.
 * Internet could drop out, users could switch from LTE to WIFI, they could leave a game, etc.
 *
 * If the server initiated one of these disconnects, or is otherwise aware of it (due to a timeout or error),
 * then the disconnect will be handled by closing the UNetConnection and notifying the game.
 * At that point, it's up to a game to decide whether or not they support Join In Progress or Rejoins.
 * If the game does support it, we will completely restart the handshaking flow as above.
 *
 * If something just briefly interrupts the client's connection, but the server is never made aware,
 * then the engine / game will typically recover automatically (albeit with some packet loss / lag spike).
 *
 * However, if the Client's IP Address or Port change for any reason, but the server isn't aware of this,
 * then we will begin a recovery process by redoing the low level handshake. In this case, game code
 * will not be alerted.
 *
 * This process is covered in StatlessConnectionHandlerComponent.cpp.
 *
 *
 *****************************************************************************************
 *****************************************************************************************
 *****************************************************************************************
 * Data Transmission
 *****************************************************************************************
 *****************************************************************************************
 *****************************************************************************************
 *
 *
 * Game NetConnections and NetDrivers are generally agnostic to the underlying communication method / technology used.
 * That is is left up to subclasses to decide (classes such as UIpConnection / UIpNetDriver or UWebSocketConnection / UWebSocketNetDriver).
 *
 * Instead, UNetDriver and UNetConnection work with Packets and Bunches.
 *
 * Packets are blobs of data that are sent between pairs of NetConnections on Host and Client.
 * Packets consist of meta data about the packet (such as header information and acknowledgments), and Bunches.
 *
 * Bunches are blobs of data that are sent between pairs of Channels on Host and Client.
 * When a Connection receives a Packet, that packet will be disassembled into individual bunches.
 * Those bunches are then passed along to individual Channels to be processed further.
 *
 * A Packet may contain no bunches, a single bunch, or multiple bunches.
 * Because size limits for bunches may be larger than the size limits of a single packet, UE supports
 * the notion of partial bunches.
 *
 * When a bunch is too large, before transmission we will slice it into a number of smaller bunches.
 * these bunches will be flagged as PartialInitial, Partial, or PartialFinal. Using this information,
 * we can reassemble the bunches on the receiving end.
 *
 *	Example: Client RPC to Server.
 *		- Client makes a call to Server_RPC.
 *		- That request is forwarded (via NetDriver and NetConnection) to the Actor Channel that owns the Actor on which the RPC was called.
 *		- The Actor Channel will serialize the RPC Identifier and parameters into a Bunch. The Bunch will also contain the ID of its Actor Channel.
 *		- The Actor Channel will then request the NetConnection send the Bunch.
 *		- Later, the NetConnection will assemble this (and other) data into a Packet which it will send to the server.
 *		- On the Server, the Packet will be received by the NetDriver.
 *		- The NetDriver will inspect the Address that sent the Packet, and hand the Packet over to the appropriate NetConnection.
 *		- The NetConnection will disassemble the Packet into its Bunches (one by one).
 *		- The NetConnection will use the Channel ID on the bunch to Route the bunch to the corresponding Actor Channel.
 *		- The ActorChannel will them disassemble the bunch, see it contains RPC data, and use the RPC ID and serialized parameters
 *			to call the appropriate function on the Actor.
 *
 *
 *****************************************************************************************
 * Reliability and Retransmission
 *****************************************************************************************
 *
 *
 * UE Networking typically assumes reliability isn't guaranteed by the underlying network protocol.
 * Instead, it implements its own reliability and retransmission of both packets and bunches.
 *
 * When a NetConnection is established, it will establish a Sequence Number for its packets and bunches.
 * These can either be fixed, or randomized (when randomized, the sequence will be sent by the server).
 *
 * The packet number is per NetConnection, incremented for every packet sent, every packet will include its packet number,
 * and we will never retransmit a packet with the same packet number.
 *
 * The bunch number is per Channel, incremented for every **reliable** bunch sent, and every **reliable** bunch will
 * include its bunch number. Unlike packets, though, exact (reliable) bunches may be retransmitted. This means we
 * will resend bunches with the same bunch number.
 *
 * Note, throughout the code what are described above as both bunch numbers and packet numbers are commonly referred to
 * just as sequence numbers. We make the distinction here for clearer understanding.
 *
 *	--- Detecting Incoming Dropped Packets ---
 *
 *
 *	By assigning packet numbers, we can easily detect when incoming packets are lost.
 *	This is done simply by taking the difference between the last successfully received packet number, and the
 *	packet number of the current packet being processed.
 *
 *	Under good conditions, all packets will be received in the order they are sent. This means that the difference will
 *	be +1.
 *
 *	If the difference is greater than 1, that indicates that we missed some packets. We will just
 *	assume that the missing packets were dropped, but consider the current packet to have been successfully received,
 *	and use its number going forward.
 *
 *	If the difference is negative (or 0), that indicates that we either received some packets out of order, or an external
 *	service is trying to resend data to us (remember, the engine will not reuse sequence numbers).
 *
 *	In either case, the engine will typically ignore the missing or invalid packets, and will not send ACKs for them.
 *
 *	We do have methods for "fixing" out of order packets that are received on the same frame.
 *	When enabled, if we detect missing packets (difference > 1), we won't process the current packet immediately.
 *	Instead, it will add it to a queue. The next time we receive a packet successfully (difference == 1), we will
 *	see if the head of our queue is properly ordered. If so, we will process it, otherwise we will continue
 *	receiving packets.
 *
 *	Once we've read all packets that are currently available, we will flush this queue processing any remaining packets.
 *	Anything that's missing at this point will be assumed to have been dropped.
 *
 *	Every packet successfully received will have its packet number sent back to the sender as an acknowledgment (ACK).
 *
 *
 *	--- Detecting Outgoing Dropped Packets ---
 *
 *
 *	As mentioned above, whenever a packet is received successfully the recipient will send back an ACK.
 *	These ACKs will contain the packet numbers of successfully received packets, in sequence order.
 *
 *	Similar to how the recipient tracks the packet number, the sender will track the highest ACKed packet number.
 *
 *	When ACKs are being processed, any ACK below our last received ACK is ignored and any gaps in packet
 *	numbers are considered Not Acknowledged (NAKed).
 *
 *	It is the sender's responsibility to handle these ACKs and NAKs and resend any missing data.
 *	The new data will be added to new outgoing packets (again, we will not resend packets we've already sent,
 *	or reuse packet sequence numbers).
 *
 *
 *	--- Resending Missing Data ---
 *
 *
 *	As mentioned above, packets alone don't contain useful game data. Instead, it's the bunches that comprise them
 *	that have meaningful data.
 *
 *	Bunches can either be marked as Reliable or Unreliable.
 *
 *	The engine will make no attempt at resending unreliable bunches if they are dropped. Therefore, if bunches
 *	are marked unreliable, the game / engine should be able to continue without them, or external retry
 *	mechanisms must be put in place, or the data must be sent redundantly. Therefore, everything below only
 *	applies to reliable bunches.
 *
 *	However, the engine will attempt to resend reliable bunches. Whenever a reliable bunch is sent, it will
 *	be added to a list of un-ACKed reliable bunches. If we receive a NAK for a packet that contained the bunch,
 *	the engine will retransmit an exact copy of that bunch. Note, because bunches may be partial, dropping even
 *	a single partial bunch will result in retransmission of the entire bunch. When all packets containing a bunch
 *	have been ACKed, we will remove it from the list.
 *
 *	Similar to packets, we will compare the bunch number for received reliable bunches to the last successfully
 *	received bunch. If we detect that the difference is negative, we simply ignore the bunch. If the difference
 *	is greater than one, we will assume we missed a bunch. Unlike packet handling, we will not discard this data.
 *	Instead, we will queue the bunch and pause processing of **any** bunches, reliable or unreliable.
 *	Processing will not be resumed until we detect have received the missing bunches, at which point we will process
 *	them, and then start processing our queued bunches.
 *	Any new bunches that are received while waiting for the missing bunches, or while we still have any bunches in our
 *	queue, will be added to the queue instead of being processed immediately.
 *
 */
```

/\*\* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* NetDrivers, NetConnections, 그리고 Channels \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* \* \* UNetDrivers는 UNetConnection 집합과 그들 사이에 공유될 수 있는 데이터를 관리하는 책임이 있습니다. \* 주어진 게임에 대해 일반적으로 상대적으로 적은 수의 UNetDrivers가 있습니다. 이들에는 일반적으로 다음이 포함됩니다: \* - 표준 게임 네트워크 트래픽을 담당하는 Game NetDriver입니다. \* - 이전에 기록된 게임 데이터를 기록하거나 재생하는 데 책임이 있는 Demo NetDriver입니다. 이것이 Replay가 작동하는 방식입니다. \* - "정상적인" 게임플레이 트래픽 외의 네트워크 트래픽을 담당하는 Beacon NetDriver입니다. \* \* 게임 또는 응용 프로그램에서 사용할 사용자 정의 NetDrivers도 구현할 수 있고 사용할 수 있습니다. \* NetConnections은 게임에 연결된 개별 클라이언트를 나타냅니다 (또는 더 일반적으로 NetDriver에 연결됩니다). \* \* 엔드포인트 데이터는 NetConnections에서 직접 처리되지 않습니다. 대신 NetConnections는 데이터를 채널로 라우팅합니다. \* 각 NetConnection은 고유한 채널 세트를 가지게 됩니다. \* \* 일반적인 채널 유형: \* \* - 제어 채널은 연결의 상태에 대한 정보를 보내는 데 사용됩니다 (연결을 닫아야 하는지 여부 등). \* - 음성 채널은 클라이언트와 서버 간에 음성 데이터를 보낼 때 사용될 수 있습니다. \* - 고유한 액터 채널은 서버에서 클라이언트로 복제된 모든 액터에 대해 존재합니다. \* \* 특수 목적으로 사용자 정의 채널도 생성하여 사용할 수 있습니다 (하지만 이는 매우 흔하지 않습니다). \* \* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* 게임 네트워크 드라이버, 네트워크 연결 및 채널 \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* \* \* 보통은 "표준" 게임 트래픽 및 연결을 위해 클라이언트와 서버에 각각 하나의 NetDriver가 있습니다. \* \* 서버 NetDriver는 게임에 참여하는 각 플레이어를 나타내는 NetConnections 목록을 유지합니다. 이는 \* 액터 데이터를 복제하는 데 책임이 있습니다. \* \* 클라이언트 NetDrivers는 서버에 대한 연결을 나타내는 단일 NetConnection을 갖게 됩니다. \* \* 서버 및 클라이언트 모두에서 NetDriver는 네트워크에서 패킷을 수신하고 해당 패킷을 적절한 \* NetConnection에 전달하고 필요할 때 새로운 NetConnections를 설정하는 데 책임이 있습니다. \* \* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* 연결 초기화 / 핸드셰이크 흐름. \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* \* \* UIpNetDriver 및 UIpConnection (또는 파생된 클래스)은 거의 모든 플랫폼에 대한 엔진 기본값입니다. \* 아래에 설명된 모든 내용은 연결을 설정하고 관리하는 방법에 대한 것입니다. 그러나 NetDriver 구현에 따라 이러한 프로세스는 달라질 수 있습니다. \* \* 서버 및 클라이언트 모두에 자체 NetDrivers가 있으며 모든 UE 복제 게임 트래픽은 IpNetDriver에서 \* 보내거나 받습니다. 이 트래픽에는 연결 설정 및 다시 연결 설정 로직도 포함됩니다. \* \* 핸드셰이킹은 다양한 위치에 분할되어 있습니다: NetDriver, PendingNetGame, World, PacketHandlers 및 기타 여러 곳입니다. \* 이 분할은 "UE-프로토콜"을 사용하여 들어오는 연결이 데이터를 보내고 있는지 여부, 주소가 악의적인 것으로 보이는지 여부, \* 특정 클라이언트가 게임의 올바른 버전을 가지고 있는지 여부 등과 같은 것들을 분리합니다. \* \* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* 시작 및 핸드셰이킹 \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* \* \* 서버가 지도를 로드할 때마다 (UEngine::LoadMap를 통해), 우리는 UWorld::Listen으로 호출합니다. \* 해당 코드는 주요 게임 네트워크 드라이버를 생성하고 설정을 파싱하며 UNetDriver::InitListen을 호출하는 책임이 있습니다. \* 최종적으로 해당 코드는 클라이언트 연결을 어떻게 듣는지를 정확하게 파악하는 것을 책임집니다. \* 예를 들어, IpNetDriver에서는 구성된 소켓 서브시스템에 대한 호출을 통해 바인딩할 IP / 포트를 결정합니다. \* \* 서버가 수신 대기 상태인 경우 클라이언트 연결을 수락할 준비가되어 있습니다. \* \* 클라이언트가 서버에 참여하려고 할 때마다, 우선 UEngine::Browse에서 서버 IP를 사용하여 새로운 UPendingNetGame를 설정합니다. \* UPendingNetGame::Initialize 및 UPendingNetGame::InitNetDriver는 설정을 초기화하고 NetDriver를 설정하는 책임이 있습니다. \* 클라이언트는이 초기화의 일부로 서버에 대한 UNetConnection을 즉시 설정하고 해당 연결을 통해 서버로 데이터를 보내기 시작하여 \* 핸드셰이킹 프로세스를 시작합니다. \* \* 클라이언트와 서버 모두에서 UNetDriver::TickDispatch가 일반적으로 네트워크 데이터를 수신하는 데 책임이 있습니다. \* 일반적으로 패킷을 수신하면 해당 주소를 검사하고 이미 알고있는 연결에서 온 것인지 여부를 확인합니다. \* 주어진 소스 주소에 대한 연결을 설정했는지 여부를 확인하기 위해 FInternetAddr에서 UNetConnection으로의 맵을 단순히 유지함으로써 결정합니다. \* \* 패킷이 이미 설정된 연결에서 왔으면 UNetConnection::ReceivedRawPacket을 통해 패킷을 해당 연결로 전달합니다. \* 패킷이 이미 설정된 연결에서 오지 않은 경우 "연결 없음"으로 처리하고 핸드셰이킹 프로세스를 시작합니다. \* \* 이 핸드셰이킹이 작동하는 방법에 대한 자세한 내용은 StatelessConnectionHandlerComponent.cpp를 참조하십시오. \* \* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* UWorld / UPendingNetGame / AGameModeBase 시작 및 핸드셰이킹 \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* \* \* 클라이언트 및 서버에서 UNetDriver 및 UNetConnection이 핸드셰이킹 프로세스를 완료하면 \* UPendingNetGame::SendInitialJoin이 클라이언트에서 호출되어 게임 레벨 핸드셰이킹을 시작합니다. \* \* 게임 레벨 핸드셰이킹은 더 구조화되고 관련된 일련의 FNetControlMessages를 통해 수행됩니다. \* 제어 메시지의 전체 세트는 DataChannel.h에서 찾을 수 있습니다. \* \* 이러한 제어 메시지를 처리하는 대부분의 작업은 UWorld::NotifyControlMessage 또는 \* UPendingNetGame::NotifyControlMessage에서 수행됩니다. 간략히 말하면 흐름은 다음과 같습니다: \* \* 클라이언트의 UPendingNetGame::SendInitialJoin이 NMT\_Hello를 보냅니다. \* \* 서버의 UWorld::NotifyControlMessage가 NMT\_Hello를 수신하고 NMT\_Challenge를 보냅니다. \* \* 클라이언트의 UPendingNetGame::NotifyControlMessage가 NMT\_Challenge를 수신하고 NMT\_Login에서 데이터를 보냅니다. \* \* 서버의 UWorld::NotifyControlMessage가 NMT\_Login을 수신하고 도전 데이터를 확인한 다음 AGameModeBase::PreLogin을 호출합니다. \* PreLogin에서 오류가보고되지 않으면 서버는 UWorld::WelcomePlayer를 호출하고 AGameModeBase::GameWelcomePlayer를 호출하여 맵 정보와 함께 NMT\_Welcome을 보냅니다. \* \* 클라이언트의 UPendingNetGame::NotifyControlMessage가 NMT\_Welcome을 수신하고 맵 정보를 읽어들입니다 (나중에 로드를 시작할 수 있도록). \* 그런 다음 구성된 클라이언트의 네트워크 속도와 함께 NMT\_NetSpeed 메시지를 보냅니다. \* \* 서버의 UWorld::NotifyControlMessage가 NMT\_NetSpeed를 수신하고 연결의 네트워크 속도를 적절하게 조정합니다. \* \* 이 시점에서 핸드셰이킹은 완료된 것으로 간주되며 플레이어는 게임에 완전히 연결됩니다. \* 맵을로드하는 데 걸리는 시간에 따라 클라이언트가 여전히 UPendingNetGame에서 일부 핸드셰이크 제어 메시지를 \* 수신 할 수 있습니다. 제어가 UWorld로 전환되기 전에 \* \* 원하는 경우 암호화를 처리하는 추가 단계도 있습니다. \* \* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* 연결 잃어버린 연결 다시 설정하기 \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* \* \* 게임 진행 중에 연결이 여러 이유로 끊길 수 있습니다. \* 인터넷 연결이 끊어질 수 있고 사용자가 LTE에서 WIFI로 전환할 수 있으며 게임을 나갈 수 있습니다. \* \* 서버가 이러한 연결 중 하나를 시작하거나 (타임아웃이나 오류로 인한) 다른 방식으로 인식하면 \* 연결이 닫히고 게임에 통보됩니다. \* 그 시점에서 게임은 Join In Progress 또는 Rejoin을 지원하는지 여부를 결정합니다. \* 게임이 지원하는 경우 우리는 위의 핸드셰이킹 흐름을 완전히 다시 시작할 것입니다. \* \* 클라이언트의 연결이 잠시 끊어지면서도 서버가 이를 인식하지 못하는 경우 \* 그러면 엔진 / 게임은 일반적으로 자동으로 복구합니다 (그러나 일부 패킷 손실 / 레이트 스파이크가 발생할 수 있음). \* \* 그러나 클라이언트의 IP 주소나 포트가 어떤 이유로 변경되지만 서버가 이를 인식하지 못하는 경우 \* 그런 다음 저수준 핸드셰이킹을 다시 수행하여 복구 프로세스를 시작합니다. 이 경우 게임 코드 \* 경고되지 않습니다. \* \* 이 프로세스는 StatlessConnectionHandlerComponent.cpp에서 다루어집니다. \* \* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* 데이터 전송 \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* \* \* 게임 NetConnections 및 NetDrivers는 기본 통신 방법 / 기술에 대해 일반적으로 중립적입니다. \* 이것은 하위 클래스가 결정하도록 남겨집니다 (UIpConnection / UIpNetDriver 또는 UWebSocketConnection / UWebSocketNetDriver와 같은 클래스). \* \* 대신, UNetDriver 및 UNetConnection은 패킷과 묶음으로 작업합니다. \* \* 패킷은 호스트 및 클라이언트 간의 네트워크 연결 사이에서 보내지는 데이터 덩어리입니다. \* 패킷은 패킷에 대한 메타 데이터 (헤더 정보 및 확인)와 묶음을 포함합니다. \* \* 묶음은 호스트 및 클라이언트 간의 채널 사이에서 보내지는 데이터 덩어리입니다. \* 연결이 패킷을 수신하면 해당 패킷은 개별 묶음으로 분해됩니다. \* 그 묶음은 그런 다음 개별 채널로 전달되어 추가 처리됩니다. \* \* 패킷은 묶음을 포함하지 않을 수 있고, 단일 묶음 또는 여러 묶음을 포함할 수 있습니다. \* 묶음의 크기 제한이 단일 패킷의 크기 제한보다 큰 경우를 고려하여 UE는 부분적인 묶음의 개념을 지원합니다. \* \* 묶음이 너무 큰 경우, 전송 전에 여러 개의 더 작은 묶음으로 슬라이스합니다. \* 이러한 묶음은 부분적인 초기, 부분적 또는 부분적 최종로 플래그가 지정됩니다. 이 정보를 사용하여 \* 수신 측에서 묶음을 다시 조립할 수 있습니다. \* \* 예: 클라이언트에서 서버로 RPC. \* - 클라이언트가 Server\_RPC를 호출합니다. \* - 해당 요청은 (NetDriver 및 NetConnection을 통해) RPC가 호출된 액터를 소유하는 액터 채널로 전달됩니다. \* - 액터 채널은 RPC 식별자와 매개변수를 묶음으로 직렬화합니다. 묶음에는 해당 Actor 채널의 ID도 포함됩니다. \* - 그런 다음 액터 채널은 NetConnection에게 묶음을 보내도록 요청합니다. \* - 나중에 NetConnection은이 (및 기타) 데이터를 패킷으로 조립하고 서버로 보낼 것입니다. \* - 서버에서 패킷은 NetDriver에 의해 수신됩니다. \* - NetDriver는 패킷을 보낸 주소를 검사하고 패킷을 적절한 NetConnection에게 전달합니다. \* - NetConnection은 패킷을 묶음으로 분해합니다 (하나씩). \* - NetConnection은 묶음의 채널 ID를 사용하여 해당하는 액터 채널로 묶음을 라우팅합니다. \* - 액터 채널은 묶음을 분해하고 RPC 데이터가 포함되어 있는지 확인하고 RPC ID 및 직렬화된 매개변수를 사용하여 \* Actor에서 해당하는 함수를 호출합니다. \* \* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* 신뢰성 및 재전송 \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* \* \* UE 네트워킹은 일반적으로 기본 네트워크 프로토콜에서 신뢰성이 보장되지 않는다고 가정합니다. \* 대신, 패킷과 묶음의 신뢰성 및 재전송을 자체적으로 구현합니다. \* \* NetConnection이 설정되면 해당 패킷 및 묶음에 대한 일련 번호를 설정합니다. \* 이것들은 고정 될 수도 있고 (고정 된 경우, 순서는 서버에서 보내집니다), \* \* 패킷 번호는 NetConnection 당이며, 보낸 모든 패킷마다 증가하며, 모든 패킷에는 해당 패킷 번호가 포함되며, \* 동일한 패킷 번호로 패킷을 다시 전송하지 않습니다. \* \* 묶음 번호는 채널 당이며, <b>신뢰할 수있는</b> 묶음마다 증가하며, <b>신뢰할 수있는</b> 묶음은 \* 해당 묶음 번호가 포함됩니다. 그러나 패킷과 달리 정확한 (신뢰할 수있는) 묶음은 다시 전송 될 수 있습니다. 이것은 \* 동일한 묶음 번호로 묶음을 다시 전송 할 것입니다. \* \* 코드 전체에서 위에서 설명한 것처럼 묶음 번호와 패킷 번호 모두 단순히 순차 번호로 참조됩니다. 여기서는 더 명확한 이해를 위해 구별합니다. \* \* --- 수신된 드롭된 패킷 감지 --- \* \* \* 패킷 번호를 할당함으로써 우리는 들어오는 패킷이 손실되었는지 쉽게 감지 할 수 있습니다. \* 이것은 마지막으로 받은 패킷보다 큰 패킷 번호를 가진 패킷을받은 경우로 간주됩니다. \* 이 경우, 드라이버가 손실된 패킷에 대한 재전송을 요청합니다. \* \* --- 수신된 드롭된 묶음 감지 --- \* \* \* 묶음 번호를 할당함으로써 우리는 들어오는 묶음이 손실되었는지 쉽게 감지 할 수 있습니다. \* 만약 마지막으로 받은 묶음 번호보다 1 큰 묶음을 수신한 경우 손실된 것으로 간주됩니다. \* 이 경우, 드라이버가 손실된 묶음에 대한 재전송을 요청합니다. \* \* --- 수신된 드롭된 부분적인 묶음 감지 --- \* \* \* 부분적 또는 부분적 최종 묶음이 손실되면 이를 감지하기가 더 어려울 수 있습니다. \* 따라서 여기에는 패킷 번호 및 묶음 번호에서의 마지막 재전송을 사용하여 처리하는 추가 로직이 포함됩니다. \* \* --- 재전송이 필요한 패킷 및 묶음 --- \* \* \* UNetDriver는 재전송이 필요한 모든 패킷과 묶음을 추적합니다. \* 손실된 패킷을 수신하면 해당 패킷을 재전송하고, 묶음이 손실된 경우 해당 묶음에있는 모든 패킷을 재전송합니다. \* \* --- 재전송 간격 --- \* \* \* 재전송 간격은 일반적으로 손실되었다고 가정되는 패킷 및 묶음에 대한 재전송 간격입니다. \* 일반적으로 TCP의 지수 백오프 알고리즘과 유사한 로직을 사용하여이 값을 결정합니다. \* 재전송 시간이 각 재전송 후 지수적으로 증가하므로 네트워크 장애가 일시적 인 경우 \* 다수의 재전송을 유발하지 않습니다. \* \* --- 제한적인 실패 --- \* \* \* 재전송 횟수에 제한을 두는 것이 중요합니다. 네트워크 장애가있는 경우 \* 계속해서 동일한 패킷을 전송하려고 시도하면 문제를 야기 할 수 있습니다. \* 따라서 재전송 시도 횟수에는 제한이 있습니다. \* \* 이러한 감지 및 재전송 메커니즘은 UE4의 가장 중요한 네트워킹 시스템 중 하나입니다. \* 이는 네트워크 연결의 신뢰성을 유지하고 게임이 지속적으로 실행되는 데 필수적입니다. \* \* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* RPC (Remote Procedure Call) \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* \* \* RPC는 게임 서버에서 클라이언트로 또는 클라이언트에서 게임 서버로 호출되는 함수입니다. \* \* RPC는 다양한 상황에서 사용됩니다. 예를 들어, 플레이어가 총을 발사하거나, 플레이어의 위치를 업데이트하거나, \* 특정 상호 작용이 게임 상태에 영향을 미치는 동안 서버 또는 클라이언트 측에서 실행해야하는 모든 유형의 작업입니다. \* \* RPC는 메시지로써 게임 서버 및 클라이언트 간에 교환됩니다. 이러한 메시지는 네트워크 통신을 통해 \* 게임 서버 또는 클라이언트로 보내지며, 이러한 호출에는 게임 상태를 변경하는 기능을 실행하는 것이 포함됩니다. \* \* RPC는 보통 UFUNCTION 매크로로 지정되는 특정 함수로 정의되며, 해당 함수는 네트워크에서 호출 될 수 있도록 준비됩니다. \* RPC 호출은 기본적으로 게임의 내부 로직에서 호출되지만 이러한 호출은 게임의 상태를 변경하는 데 사용됩니다. \* \* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* 동기화된 액터 상태 \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \* \* \* RPC가 게임 서버에서 클라이언트로 또는 클라이언트에서 게임 서버로 호출될 때 주요 목적 중 하나는 액터의 상태를 동기화하는 것입니다. \* 이것은 일반적으로 특정 액터의 위치, 회전, 스케일 등의 변경 사항을 전파하는 데 사용됩니다. \* \* 액터의 상태를 동기화하는 경우, 서버에서 상태 변경이 발생하면 해당 변경 사항을 모든 관련 클라이언트에 알리기 위해 \* RPC를 사용할 수 있습니다. 마찬가지로 클라이언트에서 상태 변경이 발생하면 이를 서버에 알리기 위해 RPC를 사용할 수 있습니다. \* \* \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* \*/

</details>

<details>
<summary>요약</summary>

<b>구글 AI요약</b>

---

This section of NetDriver.h explains how Unreal Engine manages network connections and data transfer for multiplayer games. Here's a breakdown of the key points:

<b>Components:</b>

- <b>NetDrivers:</b> Manage sets of <b>NetConnections</b> and the data they share.
- <b>NetConnections:</b> Represent individual clients connected to a game.
- <b>Channels:</b> Routes data between <b>NetConnections</b>. Each connection has different channels, like control, voice, and actor channels.

<b>Handshake Flow:</b>

- Server listens for connections, clients initiate them.
- Handshake involves verifying addresses, protocols, and game versions.
- Both server and client use <b>UNetDriver</b> for standard game traffic.

<b>Data Transmission:</b>

- Packets carry data between connections, containing meta-data and <b>Bunches</b>.
- Bunches hold the actual game data and can be reliable or unreliable (retransmitted).
- Channels receive bunches and process their data (e.g., calling RPCs on actors).

<b>Reliability and Retransmission:</b>

- Unreal Engine implements its own reliability for packets and bunches.
- Sequence numbers track order and detect missing/out-of-order data.
- Unreliable bunches are not guaranteed to arrive but should be handled by the game.
- Reliable bunches are retransmitted if not acknowledged by the recipient.

<b>Additional Notes:</b>

- This summary captures the main points; the actual code contains more details.
- Different NetDriver implementations (like UIpNetDriver) have specific ways of handling connections and data.
- The comments also cover scenarios like lost connections and rejoining games.

---

<b>NetDriver.h</b>는 언리얼 엔진의 멀티플레이어 네트워킹 시스템에 대한 주요 정보를 담고 있습니다. 아래는 주석의 주요 내용을 요약한 것입니다.

<b>구성 요소:</b>

<ul>
<li>
<b>NetDriver:</b> 여러 <b>NetConnection</b>과 그들이 공유하는 데이터를 관리합니다.

- 용도에 따라 패킷을 처리하는 다양한 NetDriver 클래스 제공한다.
  <b>GameNetDriver </b>: 게임 데이터를 처리하는데 사용되는 네트워크 드라이버

  <b>DemoNetDriver </b>: 게임 리플레이 데이터를 처리하는데 사용되는 네트워크 드라이버

  <b>BeaconNetDriver </b>: 게임 외 데이터를 처리하는데 사용되는 네트워크 드라이버

- 언리얼 엔진에서는 게임 데이터를 처리하는 GameNetDriver로<br /><b>IPNetDriver </b>클래스(IP주소 기반으로 네트워크 통신을 담당)를 사용한다.
</li>
<li>
<b>NetConnection:</b> 게임에 연결된 개별 클라이언트를 나타냅니다. <br />데이터를 직접 처리하지 않고 채널로 라우팅합니다.
</li>
<li>
<b>Channel:</b> 특정 데이터 유형에 대한 전용 경로입니다. <br />NetConnection 사이의 데이터를 라우팅합니다. 

- 일반적인 유형:
  - 제어 채널
  - 음성 채널
  - 복제된 액터를 위한 고유한 액터 채널
</li>
</ul>

<b>연결 및 핸드쉐이킹:</b>

- <b>연결</b>
  - <b>서버:</b>
    - NetConnection 목록(플레이어)을 유지 관리하고 액터 데이터를 복제합니다.
  - <b>클라이언트:</b>
    - 서버에 대한 단일 NetConnection을 가지고 있으며 NetDriver를 통해 패킷을 수신합니다.
- <b>핸드쉐이킹</b>
  - 서버는 연결을 수신 대기하고 클라이언트는 연결을 시작합니다.
  - 핸드쉐이크는 주소, 프로토콜 및 게임 버전 확인을 포함합니다.
  - 서버와 클라이언트 모두 <b>UNetDriver</b>를 사용하여 표준 게임 트래픽을 처리합니다.
- <b>연결 손실 시 재연결</b>
  - <b>게임:</b>
    - 연결을 닫고 재가입을 허용하여 연결 끊김을 처리할 수 있습니다.
  - <b>서버 인식:</b>
    - 짧은 중단은 자동으로 복구될 수 있지만 IP/포트 변경은 더 낮은 수준에서 복구를 트리거합니다.

<b>데이터 전송:</b>

- <b>Packet</b>은 연결 간 데이터를 전송하며 메타데이터와 <b>Bunch</b>를 포함합니다.
- <b>Bunch</b>는 실제 게임 데이터를 보유하며 신뢰할 수 있거나 신뢰할 수 없습니다.
  - 손실시 재 전송
  - 배송 보장 없음
- <b>Channel</b>은 <b>Bunch</b>를 수신하고 데이터를 처리합니다 (예: 액터에서 RPC 호출).
  - 언리얼 엔진에서 Bunch를 처리하는데 사용하는 주요 채널
    <b>ControlChannel</b> : 클라이언트 서버 간의 커넥션을 다룰 때 사용하는 채널<br />(초기 접속에 관련된 데이터 패킷을 분석한다)

    <b>ActorChannel </b>: 액터 리플리케이션 작업을 다룰 때 사용하는 채널

    <b>VoidChannel </b>: 음성 데이터를 전달할 때사 용

<b>신뢰성 및 재전송:</b>

- 언리얼 엔진은 패킷과 <b>Bunch</b>에 대한 자체적인 신뢰성을 구현합니다.
- 시퀀스 번호는 순서를 추적하고 누락된/잘못된 데이터를 감지합니다.
- 신뢰할 수 없는 <b>Bunch</b>는 도착하지 않을 수 있지만 게임에서 처리해야 합니다.
- 신뢰할 수 있는 <b>Bunch</b>는 수신자가 확인하지 않으면 재전송됩니다.

<b>참고 사항:</b>

- 이 요약은 주요 내용을 담고 있으며 실제 코드에는 더 많은 세부 정보가 포함됩니다.
- UIpNetDriver와 같은 다른 <b>NetDriver</b> 구현은 연결 및 데이터 처리에 대한 고유한 방식을 가지고 있습니다.
- 주석은 연결 손실 및 다시 참여와 같은 시나리오도 다룹니다.

</details>
