import { useEffect, useState } from "react"
import { io } from "socket.io-client"

import Dashboard from "./components/Dashboard"
import ContactPage from "./components/ContactPage"

let socket = io(window.location.origin)

function App(){
  const [contact, setContact] = useState(false)

  return (
    <>
      {
        !contact && <Dashboard socket={socket} setContact={setContact}></Dashboard>
      }
      {
        contact && <ContactPage></ContactPage>
      }
    </>
  )
}

export default App

