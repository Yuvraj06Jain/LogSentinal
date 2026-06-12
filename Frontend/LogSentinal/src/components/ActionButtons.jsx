function ActionButtons({
  pause,
  setPause,
  view,
  setView,
  from, 
  to,
}){
  return(
    <div className="flex gap-2 justify-center items-center">
      <button className="cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-blue-500/60 hover:scale-110 duration-150" onClick = {() => {summaryGen(from, to)}}>
        Get Summary
      </button>

      <input type="radio" name="view" id="History" className="hidden peer"></input>
      <label htmlFor="History" className={` cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-purple-800
      ${ view==="history"? "peer-checked:bg-purple-800" : "bg-transparent" }`} onClick = {() => setView("history")}>History</label>

      <input type="radio" name="view" id="Real Time" className="hidden peer" defaultChecked></input>
      <label htmlFor="Real Time" className={`cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-green-600/50 ${ view==="real"? "bg-green-600/50" : "bg-transparent" } `} onClick = {() => setView("real")} >Real Time</label>

      <button className={` cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-amber-400/50 ${ pause ? "bg-amber-400/80" : "bg-transparent"}`} onClick={() => setPause((prev) => !prev)}>Pause</button>
    </div>
  )
}

export default ActionButtons