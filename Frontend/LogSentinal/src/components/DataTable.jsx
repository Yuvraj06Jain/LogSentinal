function DataTable({
  logs,
  show,
  from,
  to
}){
  if(!show || !logs[show]?.length){
    return(
      <div className="w-full bg-slate-900 border border-slate-700 rounded-xl text-slate-700 text-center">
        No data available
      </div>
    )
  }

  console.log(show)
  console.log(logs[show])

  return(
    <div className="w-full bg-slate-900 border border-slate-700 rounded-xl scrollbar-none overflow-scroll max-h-105">
      <table className="w-full text-sm table-fixed">

        <thead>
          <tr className="bg zinc-900 border border-slate-700 rounded-xl scrollbar-none overflow-scroll">
            {
              Object.keys(logs[show][0]).map((e) => (
                <th key = {e} className="text-left text-xs font-medium text-slate-400 px-3 py-2">{e}</th>
              ))
            }
          </tr>
        </thead>

        <tbody>
          {
            logs[show].map((dict, index) => (
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