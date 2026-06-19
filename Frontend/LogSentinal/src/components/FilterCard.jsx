import { useState, useEffect } from "react";

function FilterCard({
  from,
  setFrom,
  to,
  setTo,
  view,
  setMessage,
  socket
}){
  
  const [custom, setCustom] = useState(false)
  
  useEffect(() => {
    if (view==="realTime")
      setCustom(false)
  },[view])

  let min = new Date(); 
  min.setDate(min.getDate() - 30); 
  min = min.toISOString().slice(0,16);
  
  return (
    <div className="rounded-xl bg-slate-900 border border-slate-700 flex justify-between items-center px-2 py-1.25 gap-4">

      <p className="text-sm text-slate-400 font-semibold">Filter Range:</p>

      <div className="flex justify-evenly flex-1 min-w-200 max-w-max">

        {
          !custom && 
          <div className="">

            <label className="text-xs text-zinc-400 m-1 font-bold">TimeFrame: </label>

            { 
              (view==="realTime") &&
              <input className="border border-slate-700 rounded-xl active:border-slate-600 bg-green-400/40 outline-none text-sm font-semibold px-5 py-0.5 text-slate-300 text-center" readOnly value={"Real Time"}></input>
            }
            { 
              (view==="historical") &&
              <>

              <select className = "text-sm  rounded-md px-2 py-0.5 outline-none bg-slate-800 border-slate-600 text-slate-200 w-40" onChange = {(e) => {
                if (e.target.value === "Custom Range") setCustom(true)
                }}>

                <option className = "cursor-pointer" onClick = {() => setFrom(() => {
                  let date = new Date()
                  setTo(date)
                  date.setDate(date.getDate() - 7)
                  setFrom(date.toISOString())
                })} >Last Week</option>

                <option className = "cursor-pointer" onClick = {() => setFrom(() => {
                  let date = new Date()
                  setTo(date)
                  date.setDate(date.getDate() - 14)
                  setFrom(date.toISOString())
                })} >Last 2 Weeks</option>

                <option className = "cursor-pointer" onClick = {() => setFrom(() => {
                  let date = new Date()
                  setTo(date)
                  date.setDate(date.getMonth() - 1)
                  setFrom(date.toISOString())
                })} >Last Month</option>

                <option className = "cursor-pointer" onClick = {() => setCustom(true)}>Custom Range</option>

              </select>

              </>
            }

          </div>
        }

        {
          custom &&
          <>

            <div className="">
              <label className="text-xs text-zinc-400 m-1 font-semibold">From: </label>
              <input type="datetime-local" className="border border-slate-700 rounded-xl active:border-slate-600 outline-none text-sm px-5 py-0.5 text-slate-300 w-80" value={from}
              min={min}
              max={to || new Date().toISOString().slice(0,16)}
              onChange={(e) => setFrom(e.target.value)}></input>
            </div>

            <div className="">
              <label className="text-xs text-zinc-400 m-1 font-semibold">To: </label>
              <input type="datetime-local" className="border border-slate-700 rounded-xl active:border-slate-600 outline-none text-sm px-5 py-0.5 text-slate-300 w-80" value={to}
              min = {from}
              max = {new Date().toISOString().slice(0,16)}
              onChange={(e) => setTo(e.target.value)}></input>
            </div>

          </>
        }
        

      </div>

      <div className=" h-full w-0 border border-slate-600"></div>
      
      { (view==="realTime") &&
        <div className="flex justify-center items-center mr-2">
          
          <button className="text-sm font-bold  rounded-lg py-2 px-3 text-slate-300 hover:bg-orange-500 hover:scale-105 duration-150 cursor-pointer border border-slate-700" onClick = {() => {
            socket.emit("Refresh", (Response) => {if (Response.Status === "Failed") setMessage(Response.Message)})
          }}>
            Refresh
          </button>

        </div>
      }

      {
        (view === "historical") &&
        <div className="flex justify-center items-center mr-2">
          
          <button className="text-sm font-bold  rounded-lg py-2 px-2 text-slate-300 hover:bg-orange-500 hover:scale-105 duration-150 cursor-pointer" onClick = {() => {
            if ((from === undefined) || (to === undefined))
              setMessage("Please select a Timeframe of which you want the data to be fetched.")
            
            socket.emit("historical", currentRoom, from, to ,(Response) => {if (Response.Status === "Failed") setMessage(Response.Message)})
          }}>
            Fetch
          </button>

        </div>
      }

    </div>
  )
}

export default FilterCard;