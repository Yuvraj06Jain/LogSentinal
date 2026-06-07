import { useEffect, useState } from "react";

function Home(){
  return(
    <div className="fixed inset-0 -z-10 bg-slate-950" style={{backgroundImage: 'radial-gradient(circle, #ffffff22 1px, transparent 1px)', backgroundSize: '24px 24px'}}>
      <div className="min-h-screen flex flex-col itmes-center justify-center gap-5 text-center">
        <h1 className="font-extrabold text-9xl cursor-pointer text-cyan-500 active:text-slate-500 duration-100 ">LogSentinal</h1>
        <p className="font-extrabold text-xl cursor-default text-slate-400 tracking-wide">Monitor your logs, Catch Threats before they catch you.</p>
      </div>
    </div>
  )
}

function Header(){
  return(
    <div className="w-screen h-10 bg-slate-950/80 backdrop-blur-sm shrink-0 mb-20 rounded-b-xl pt-3 flex justify-between items-center">

      <div classname="flex gap-2">
        <label htmlFor="logtype" className="text-sm text-slate-400 ">Active Log Monitoring : </label>
        <select id="logtype" className="text-sm  rounded-md px-2 py-0.5 outline-none bg-slate-800 border-slate-600 text-slate-200">
          <option className="">Apache Files</option>
          <option className="">Nginx Files</option>
          <option className="">Auth Files</option>
        </select>
      </div>

      <ActionButtons />

      <div className="flex justify-center items-center mr-2">
        <button className="text-sm font-bold border border-slate-700 rounded-lg py-2 px-2 text-slate-300 hover:bg-orange-500 hover:scale-105 duration-150">
          Refresh
        </button>
      </div>

    </div>
  )
}

function ActionButtons(){
  return(
    <div className="flex gap-2 justify-center items-center">
      <div>
        <button className="text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-blue-500/60 hover:scale-110 duration-150">
          Get Summary
        </button>
      </div>
      <div>
        <input type="radio" name="view" id="Pause" className="hidden peer "></input>
        <label htmlFor="Pause" className="text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-yellow-300/60 
        peer-checked:bg-yellow-300/60">Pause</label>
      </div>
      <div>
        <input type="radio" name="view" id="Resume" className="hidden peer"></input>
        <label htmlFor="Resume" className="text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-green-400/60
        peer-checked:bg-green-400/60">Resume</label>
      </div>
      <div>
        <button className="text-sm font-bold border border-slate-700 rounded-lg py-2 px-4 text-slate-300 hover:bg-red-500/60 hover:scale-110 duration-150">
          Exit
        </button>
      </div>
    </div>
  )
}


function FilterCard(){
  return(
    <div className=" rounded-xl p-4 bg-slate-900 border border-slate-700">
        <p className="text-sm text-zinc-400 mb-3">Filter range</p>
        <div className="grid grid-cols-1">
          <div className="flex-1">
            <p className="text-xs text-zinc-400 mb-1">From</p>
            <input className="border border-slate-700 rounded-xl w-70 active:border-slate-600 outline-none px-2 text-sm py-0.5 text-slate-300" placeholder="Date/Month/Year"></input>
          </div>
          <div className="flex-1">
            <p className="text-xs text-zinc-400 mb-1">To</p>
            <input className="border border-slate-700 rounded-xl w-70 active:border-slate-600 outline-none px-2 text-sm py-0.5 text-slate-300" placeholder="Date/Month/Year"></input>
          </div>
        </div>
      </div>
  )
}

function DataButtons(){
  return(
    <div className="rounded-xl p-4 bg-slate-900 border border-slate-700">
      <p className="text-xs text-slate-400 mb-3">View</p>
      <ul className="grid grid-cols-1 gap-3">
        {["Failed Logins", "Suspicious IPs", "Auth Logs", "Apache Logs", "Nginx Logs", "All Events"].map((view) => (
          <li key={view}>
            <input type="radio" name="view" id={view} className="hidden peer" />
            <label htmlFor={view} className="block text-xs border border-slate-600 text-slate-300 rounded-lg py-1.5 text-center cursor-pointer hover:bg-cyan-500/10 peer-checked:bg-cyan-500/10 peer-checked:border-cyan-500/40 peer-checked:text-cyan-400">{view}</label>
          </li>
        ))}
      </ul>
    </div>
  )
}

function DataTable(){
  return(
    <div className="bg-slate-900 border border-slate-700 rounded-xl scrollbar-none overflow-scroll max-h-105">
      <table className="w-full text-sm table-fixed">

        <thead>
          <tr className="bg-zinc-600/50 border-b border-slate-700">
            <th className="text-left text-xs font-medium text-slate-400 px-3 py-2 w-40">Timestamp</th>
            <th className="text-left text-xs font-medium text-slate-400 px-3 py-2 w-16">Level</th>
            <th className="text-left text-xs font-medium text-slate-400 px-3 py-2 w-28">IP address</th>
            <th className="text-left text-xs font-medium text-slate-400 px-3 py-2">Message</th>
          </tr>
        </thead>

        <tbody>

          <tr className="border-b border-slate-700">
            <td className="px-3 py-2 text-slate-100 text-xs">2024-06-04 12:01:35</td>
            <td className="px-3 py-2 text-xs text-yellow-500">WARN</td>
            <td className="px-3 py-2 text-slate-100 text-xs">192.168.1.10</td>
            <td className="px-3 py-2 text-slate-100 text-xs">Failed login — user: root</td>
          </tr>
    
        </tbody>
      </table>
    </div>
  )
}


function Dashboard(){
  return(
    <div className="fixed inset-0 -z-10 bg-slate-950" style={{backgroundImage: 'radial-gradient(circle, #ffffff22 1px, transparent 1px)', backgroundSize: '24px 24px'}}>
      <div className="flex flex-col h-screen">
        {/* Header */}
        <Header />

        <div className="flex gap-4 px-6 pb-6 flex-1 min-h-0">
          {/* Left panel */}
          <div className="flex flex-col gap-3 w-100 shrink-0">

            {/* Filter card */}
            <FilterCard />
            {/* Data buttons card */}
            <DataButtons />

          </div>

          {/* Right panel */}
          <div className="flex flex-col gap-3 flex-1" >

            {/* Table */}
            <DataTable />
          </div>

        </div>

    </div>

  </div>
  )
}

function App(){

  return (
    <>
      {
        false && <Home/>
      }
      {
        true && <Dashboard/>
      }
    </>
  )
}

export default App


