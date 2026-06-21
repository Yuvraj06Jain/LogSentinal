function ViewButtons({
  view,
  setView,
  from, 
  to,
  currentRoom,
  socket
}){
  return(
    <div className="flex gap-5 justify-center items-center  flex-none shrink-0">

      <input type="radio" name="view" id="History" className="hidden peer"></input>
      <label htmlFor="History" className={` cursor-pointer text-sm font-bold border border-purple-800 rounded-lg p-2 text-purple-800 hover:bg-purple-800/25 hover:scale-110 duration-150
      ${ view==="historical"? "peer-checked:bg-purple-950/50" : "bg-transparent" }`} onClick = {() => {
        socket.emit("historical", currentRoom);
        setView((prev) => {
          return {
            ...prev,
            [currentRoom] : "historical"
          };
        });
      }}>Historical Data</label>

      <input type="radio" name="view" id="Real Time" className="hidden peer" defaultChecked></input>
      <label htmlFor="Real Time" className={`cursor-pointer text-sm font-bold border border-green-600 rounded-lg p-2 text-green-600 hover:bg-green-600/20 hover:scale-110 duration-150 ${ view==="realTime"? "bg-green-950" : "bg-transparent" } `} onClick = {() => {
        setView((prev) => {
          return {
            ...prev,
            [currentRoom] : "realTime"
          };
        });
      }}>Real Time</label>

    </div>
  )
}

export default ViewButtons