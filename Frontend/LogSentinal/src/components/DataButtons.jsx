function DataButtons({
  logs,
  setShow
}){
  return(
    <div className="rounded-xl p-4 bg-slate-900 border border-slate-700">
      <p className="text-xs text-slate-400 mb-3">View</p>
      <ul className="grid grid-cols-1 gap-3">
        {
          Object.keys(logs).map((view) => (
            <li key={view}>
              <input type="radio" name="view" id={view} className="hidden peer" onClick = {() => {setShow(view)}} />
              <label htmlFor={view} className="block text-xs border border-slate-600 text-slate-300 rounded-lg py-1.5 text-center cursor-pointer hover:bg-cyan-500/10 peer-checked:bg-cyan-500/10 peer-checked:border-cyan-500/40 peer-checked:text-cyan-400">{view}</label>
            </li>
          ))
        }
      </ul>
    </div>
  )
}

export default DataButtons;