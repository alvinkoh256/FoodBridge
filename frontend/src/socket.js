import { io } from "socket.io-client";

const socket = io("http://localhost:5014", {
  transports: ["websocket"],
});

socket.on("connect", () => {
  console.log("Connected to socket server:", socket.id);
  socket.emit("joinRoom", "productListingRoom");
});

export default socket;