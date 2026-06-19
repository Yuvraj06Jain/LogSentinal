import { useEffect } from "react";

function DataButtons({
  logs,
  show,
  setShow,
  view,
  currentRoom
}){
  if (!currentRoom || !view){
    return (
      <div className="rounded-xl p-4 bg-slate-900 border border-slate-700">
        <p className="text-xs text-slate-400 mb-3 font-bold">Analyze</p>
      </div>
    )
  }


  return(

    <div className="rounded-xl p-4 bg-slate-900 border border-slate-700">

      <p className="text-xs text-slate-400 mb-3 font-bold">Analyze</p>

      <ul className="grid grid-cols-1 gap-3">
        {
          
          Object.keys(logs).map((field) => (
            <li key={field}>
              <input type="radio" name="field" id={field} className="hidden peer" checked={show[currentRoom][view]===field} readOnly
              onClick={() => {
                setShow((prev) => {return {
                  ...prev, [currentRoom]: {
                    ...prev[currentRoom], [view] : field
                  }
                };
              });
              }} />

              <label htmlFor={field} className="block text-xs border border-slate-600 text-slate-300 rounded-lg py-1.5 text-center cursor-pointer hover:bg-cyan-500/10 
              peer-checked:bg-cyan-500/10 peer-checked:border-cyan-500/40 peer-checked:text-cyan-400">{field}</label>

            </li>
          ))

        }
      </ul>

    </div>
  )

}

export default DataButtons;