function DataTable({
  logs,
  show,
  setShow,
  view,
  currentRoom, 
  from,
  to
}){
  if (!currentRoom || !show[currentRoom] || !show[currentRoom][view]){
    return (
      <div className="w-full bg-[#101720] border border-[#1c2630] rounded-xl text-[#1c2630] text-center py-2">

      </div>
    )
  } 

  const data = logs[show[currentRoom][view]]

  // if ( view === "historical" && typeof logs !== 'object'){
  //   return(
  //     <div className="w-full h-105 bg-[#101720] border border-[#1c2630] rounded-xl text-center py-2 flex flex-col justify-center items-center">
  //       <p className="text-7xl font-extrabold text-[#ff4d5e]">X</p>
  //       <p className="text-2xl font-extrabold text-[#f2a93b]">No Historical Data Found</p>
  //     </div>
  //   )
  // }
  if(!data || data.length === 0){
    return(
      <div className="w-full bg-[#101720] border border-[#1c2630] rounded-xl text-[#1c2630] text-center py-2">
          No Data Present
      </div>
    )
  }

  return(
    <div className="w-full bg-[#101720] border border-[#1c2630] rounded-xl scrollbar-none overflow-scroll max-h-115 font-['JetBrains_Mono']">
      <table className="w-full text-sm table-fixed">
        <thead>
          <tr className="bg zinc-900 border border-[#1c2630] rounded-xl scrollbar-none overflow-scroll">
            {
              Object.keys(data[0]).map((e) => (
                <th key = {e} className="text-left text-xs font-medium text-[#d7e4dd]/60 px-3 py-2">{e}</th>
              ))
            }
          </tr>
        </thead>

        <tbody>
          {
            data.map((dict, index) => (
              <tr key={index} className="border-b border-[#1c2630]">
                {
                  Object.values(dict).map((value, i) => (
                    <td key={i} className="px-3 py-2 text-[#d7e4dd] text-xs">{value}</td>
                  ))
                }
              </tr>
            ))
          }
        </tbody>

      </table>

    </div>
  )
}

export default DataTable;