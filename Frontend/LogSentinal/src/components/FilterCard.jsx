function FilterCard({
  from,
  to,
}){
  return (
    <div className="rounded-xl bg-slate-900 border border-slate-700 flex justify-between items-center px-2 py-1.25 gap-4">
      <p className="text-sm text-slate-400 font-semibold">Filter Range</p>
      <div className="flex justify-evenly flex-1 ">
        <div className="">
          <label className="text-xs text-zinc-400 m-1 font-semibold">From: </label>
          <input className="border border-slate-700 rounded-xl active:border-slate-600 outline-none text-sm px-5 py-0.5 text-slate-300 w-80" placeholder="DD/MM/YY" value={from}></input>
        </div>
        <div className="">
          <label className="text-xs text-zinc-400 m-1 font-semibold">To: </label>
          <input className="border border-slate-700 rounded-xl active:border-slate-600 outline-none text-sm px-5 py-0.5 text-slate-300 w-80" placeholder="DD/MM/YY" value={to}></input>
        </div>
      </div>
      <div className=" h-full w-0 border border-slate-600"></div>
      <div className="flex justify-center items-center mr-2">
        <button className="text-sm font-bold  rounded-lg py-2 px-2 text-slate-300 hover:bg-orange-500 hover:scale-105 duration-150 cursor-pointer" onClick = {() => {
          socket.emit("Refresh")
        }}>
          Refresh
        </button>
      </div>
    </div>
  )
}

export default FilterCard;