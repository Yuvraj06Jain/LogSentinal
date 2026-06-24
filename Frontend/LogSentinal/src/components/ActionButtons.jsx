function ActionButtons({
    setSummary,
    pause,
    setPause,
    socket,
    view,
    setHome,
    currentRoom,
}){
    return (
        <div className="flex justify-end items-center gap-7 flex-1">

            <button className="cursor-pointer text-sm font-bold border border-[#1c2630]  rounded-lg p-2 text-[#d7e4dd]/70 hover:bg-[#d7e4dd]/10 hover:scale-110 duration-150"
            onClick={() => setSummary(true)}>
                Summary Report
            </button>

            {/* <button className={` cursor-pointer text-sm font-bold border rounded-lg p-2 hover:scale-110 duration-150 ${ !pause? "border-[#f2a93b] text-[#f2a93b] hover:bg-[#f2a93b]/30" : "border-[#3cff9e] text-[#3cff9e] hover:bg-[#3cff9e]/20"} ${ view=="historical"? "opacity-50 pointer-events-none cursor-not-allowed" : "" }`} 
            onClick={() => setPause(prev => {
                return {
                    ...prev,
                    [currentRoom] : !prev[currentRoom]
                }
            })}>
                {pause? "Resume" : "Pause"}
            </button> */}

            <button className="text-sm font-bold border border-[#ff4d5e] rounded-lg py-2 px-4 text-[#ff4d5e] hover:bg-[#ff4d5e]/20 hover:scale-110 duration-150 mr-4"
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