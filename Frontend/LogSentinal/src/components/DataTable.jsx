function DataTable({
  logs,
  show,
  view,
  currentRoom, 
  from,
  to
}){
  if (!currentRoom || !show[currentRoom] || !show[currentRoom][view]){
    return (
      <div className="w-full bg-slate-900 border border-slate-700 rounded-xl text-slate-700 text-center py-2">

      </div>
    )
  } 

  const data = logs[show[currentRoom][view]]
  console.log(data)

  if ( view === "historical" && typeof logs !== 'object'){
    return(
      <div className="w-full h-105 bg-slate-900 border border-slate-700 rounded-xl text-center py-2 flex flex-col justify-center items-center">
        <p className="text-7xl font-extrabold text-red-700">X</p>
        <p className="text-2xl font-extrabold text-amber-300">No Historical Data Found</p>
      </div>
    )
  }
  else if(data && data.length === 0){
    return(
      <div className="w-full bg-slate-900 border border-slate-700 rounded-xl text-slate-700 text-center py-2">
          No Data Present
      </div>
    )
  }
  console.log(data)
  // console.log(currentRoom, show[currentRoom], show[currentRoom][view], logs[show[currentRoom][view]])
  return(
    <div className="w-full bg-slate-900 border border-slate-700 rounded-xl scrollbar-none overflow-scroll max-h-115">
      <table className="w-full text-sm table-fixed">
        <thead>
          <tr className="bg zinc-900 border border-slate-700 rounded-xl scrollbar-none overflow-scroll">
            {
              Object.keys(data[0]).map((e) => (
                <th key = {e} className="text-left text-xs font-medium text-slate-400 px-3 py-2">{e}</th>
              ))
            }
          </tr>
        </thead>

        <tbody>
          {
            data.map((dict, index) => (
              <tr key={index} className="border-b border-slate-700">
                {
                  Object.values(dict).map((value, i) => (
                    <td key={i} className="px-3 py-2 text-slate-100 text-xs">{value}</td>
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