function ActionButtons({
    setSummary,
    pause,
    setPause,
    socket,
    view,
    setHome,
    currentRoom
}){
    return (
        <div className="flex justify-end items-center gap-7 flex-1">

            <button className="cursor-pointer text-sm font-bold border border-blue-500  rounded-lg p-2 text-blue-500 hover:bg-blue-500/20 hover:scale-110 duration-150"
            onClick={() => setSummary(true)}>
                Summary Report
            </button>

            <button className={` cursor-pointer text-sm font-bold border rounded-lg p-2 hover:scale-110 duration-150 ${ !pause? "border-amber-400 text-amber-400 hover:bg-amber-400/30" : "border-green-500 text-green-500 hover:bg-green-500/20"} ${ view=="historical"? "opacity-50 pointer-events-none cursor-not-allowed" : "" }`} 
            onClick={() => setPause(prev => {
                return {
                    ...prev,
                    [currentRoom] : !prev[currentRoom]
                }
            })}>
                {pause? "Resume" : "Pause"}
            </button>

            <button className="text-sm font-bold border border-red-700 rounded-lg py-2 px-4 text-red-800 hover:bg-red-500/20 hover:scale-110 duration-150 mr-4"
            onClick = {() => {
                socket.emit("EXIT")
                setHome(true)
                socket.close()
            }}>
                Exit
            </button>
        
      </div>
    )
}

export default ActionButtons;