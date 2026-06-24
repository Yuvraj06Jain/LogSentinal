import { useState, useEffect } from "react";

function FilterCard({
  from,
  setFrom,
  to,
  setTo,
  view,
  setMessage,
  socket,
  currentRoom
}){
  
  const [custom, setCustom] = useState(false)
  
  useEffect(() => {
    if (view==="realTime")
      setCustom(false)
  },[view])

  let min = new Date(); 
  min.setDate(min.getDate() - 30); 
  min = min.toISOString().slice(0,16);

  function handleChange(val){
    let today = new Date()

    if (val === "Last Week"){
      setTo(today.toISOString())
      today.setDate(today.getDate() - 7)
      setFrom(today.toISOString())
    }
    else if (val === "Last 2 Weeks"){
      setTo(today.toISOString())
      today.setDate(today.getDate() - 14)
      setFrom(today.toISOString())
    }
    else if (val === "Last Month"){
      setTo(today.toISOString())
      today.setDate(today.getDate() - 30)
      setFrom(today.toISOString())
    }
    else if (val === "Custom Range"){
      setCustom(true)
    }
  }
  
  return (
    <div className="rounded-xl bg-[#101720] border border-[#1c2630] flex justify-between items-center px-2 py-1.25 gap-4">

      <p className="text-sm text-[#d7e4dd]/60 font-semibold">Filter Range:</p>

      <div className="flex justify-evenly flex-1 min-w-200 max-w-max">

        {
          !custom && 
          <div className="">

            <label className="text-xs text-[#d7e4dd]/60 m-1 font-bold">TimeFrame: </label>

            { 
              (view==="realTime") &&
              <input className="border border-[#1c2630] rounded-xl active:border-[#1c2630] bg-[#3cff9e]/40 outline-none text-sm font-semibold px-5 py-0.5 text-[#d7e4dd]/80 text-center" readOnly value={"Real Time"}></input>
            }
            { 
              (view==="historical") &&
              <>

              <select className = "text-sm  rounded-md px-2 py-0.5 outline-none bg-[#101720] border-[#1c2630] text-[#d7e4dd] w-40" onChange = {(e) => handleChange(e.target.value)}>
                  
                <option className="cursor-pointer">Last Week</option>

                <option className="cursor-pointer">Last 2 Weeks</option>

                <option className="cursor-pointer">Last Month</option>

                <option className = "cursor-pointer">Custom Range</option>

              </select>

              </>
            }

          </div>
        }

        {
          custom &&
          <>

            <div className="">
              <label className="text-xs text-[#d7e4dd]/60 m-1 font-semibold">From: </label>
              <input type="datetime-local" className="border border-[#1c2630] rounded-xl active:border-[#1c2630] outline-none text-sm px-5 py-0.5 text-[#d7e4dd]/80 w-80" 
              value={from.toISOString()}
              min={min}
              max={to.slice(0,16) || new Date().toISOString().slice(0,16)}
              onChange={(e) => setFrom(new Date(e.target.value).toISOString())}></input>
            </div>

            <div className="">
              <label className="text-xs text-[#d7e4dd]/60 m-1 font-semibold">To: </label>
              <input type="datetime-local" className="border border-[#1c2630] rounded-xl active:border-[#1c2630] outline-none text-sm px-5 py-0.5 text-[#d7e4dd]/80 w-80" 
              value={to.toISOString()}
              min = {from}
              max = {new Date().toISOString().slice(0,16)}
              onChange={(e) => setTo(new Date(e.target.value).toISOString())}></input>
            </div>

          </>
        }
        

      </div>

      <div className=" h-full w-0 border border-[#1c2630]"></div>
      
      { (view==="realTime") &&
        <div className="flex justify-center items-center mr-2">
          
          <button className="text-sm font-bold rounded-lg py-2 px-3 text-[#d7e4dd]/70 hover:bg-[#d7e4dd]/10 hover:scale-105 duration-150 cursor-pointer border border-[#1c2630] " 
          onClick = {() => {
            socket.emit("Refresh", (Response) => {setMessage(Response)})
          }}>
            Refresh
          </button>

        </div>
      }

      {
        (view === "historical") &&
        <div className="flex justify-center items-center mr-2">
          
          <button className="text-sm font-bold rounded-lg py-2 px-3 text-[#d7e4dd]/70 hover:bg-[#d7e4dd]/10 hover:scale-105 duration-150 cursor-pointer border border-[#1c2630]   " 
          onClick = {() => {
            if ((from === undefined) || (to === undefined)){
              setMessage({"Status" : "Info" , "Message" : "Please select a Timeframe of which you want the data to be fetched."})
              return 
            }

            socket.emit("historical", currentRoom, from, to ,(Response) => { console.log(Response); setMessage(Response);})
          }}>
            Fetch
          </button>

        </div>
      }

    </div>
  )
}

export default FilterCard;