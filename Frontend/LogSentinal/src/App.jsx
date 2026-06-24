import { useEffect, useState } from "react"
import { io } from "socket.io-client"

import Home from "./components/HomePage"
import Dashboard from "./components/Dashboard"

let socket = io("http://localhost:8000")

function App(){
  const [home, setHome] = useState(true)

  return (
    <>
      {
        false && <Home setHome={setHome}/>
      }
      {
        true && <Dashboard setHome = {setHome} socket={socket}/>
      }
    </>
  )
}

export default App

