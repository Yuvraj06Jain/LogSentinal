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
      <div className="rounded-xl p-4 bg-[#101720] border border-[#1c2630]">
        <p className="text-xs text-[#d7e4dd]/60 mb-3 font-bold">Analyze</p>
      </div>
    )
  }


  return(

    <div className="rounded-xl p-4 bg-[#101720] border border-[#1c2630]">

      <p className="text-xs text-[#d7e4dd]/60 mb-3 font-bold">Analyze</p>

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

              <label htmlFor={field} className="block text-xs border border-[#1c2630] text-[#d7e4dd]/80 rounded-lg py-1.5 text-center cursor-pointer hover:bg-[#3cff9e]/10 
              peer-checked:bg-[#3cff9e]/10 peer-checked:border-[#3cff9e]/40 peer-checked:text-[#3cff9e]">{field}</label>

            </li>
          ))

        }
      </ul>

    </div>
  )

}

export default DataButtons;