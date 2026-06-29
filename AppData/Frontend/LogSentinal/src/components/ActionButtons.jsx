function ActionButtons({
    setSummary,
    socket,
    view,
    currentRoom,
    setContact
}){
    return (
        <div className="flex justify-end items-center gap-7 flex-1">

            <button className="cursor-pointer text-sm font-bold border border-[#1c2630]  rounded-lg p-2 text-[#d7e4dd]/70 hover:bg-[#d7e4dd]/10 hover:scale-110 duration-150"
            onClick={() => setSummary(true)}>
                Summary Report
            </button>

            <button className="text-sm font-bold border border-[#ff4d5e] rounded-lg py-2 px-4 text-[#ff4d5e] hover:bg-[#ff4d5e]/20 hover:scale-110 duration-150 mr-4"
            onClick = {() => {
                socket.emit("EXIT")
                socket.close()
                setContact(true)
            }}>
                Exit
            </button>
        
      </div>
    )
}

export default ActionButtons;