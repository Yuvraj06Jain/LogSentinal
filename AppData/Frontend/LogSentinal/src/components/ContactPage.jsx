import { useState, useRef } from "react";
import MessageBox from "./MessageBox";

function ContactPage(){
    const boxInfo = {"Email" : ["yuvraj.jain@students.iiit.ac.in", ""], "LinkedIn" : ["Yuvraj Jain", "https://linkedin.com/in/yuvraj-jainn"], "GitHub" : ["Yuvraj@06Jain", "https://github.com/Yuvraj06Jain"]}

    const sbj = useRef("")
    const name = useRef("")
    const msg = useRef("")

    const [message, setMessage] = useState("")

    function sendMail(){
        if (sbj.current === "" || name.current === "" || msg.current === ""){
            setMessage({"Status" : "Failed", "Message" : "Please fill all the components"})
            return
        }

        setMessage({"Status" : "Success", "Message" : "Mail Sent"})
        window.location.href = `mailto:yuvraj.jain@students.iiit.ac.in?subject=${encodeURIComponent(sbj.current)}&body=${encodeURIComponent(`From: ${name.current}\n\n${msg.current}`)}`
    }

    return(
        <>
            <div className="fixed inset-0 -z-10 bg-[#080c14] " style={{backgroundImage: 'radial-gradient(circle, #d7e4dd22 1px, transparent 1px)', backgroundSize: '24px 24px'}}>

                <div className="min-h-screen flex flex-col items-center justify-center gap-10 ">
                    
                    <div className="">
                        <p className="font-['Audiowide'] text-8xl text-[#3cff9e] font-extrabold">Contact Me</p>
                    </div>

                    <div className="flex justify-center items-center gap-3">
                        
                        <div className="min-h-90 max-h-100 w-70 border border-dashed border-[#3cff9e]/40 rounded-3xl flex flex-col justify-between p-4 gap-3">

                            {
                                Object.keys(boxInfo).map((key) => (
                                    <div key={key} className="bg-gray-800/50 py-4 px-2 flex flex-col justify-center items-center rounded-2xl ">
                                        <p className="text-[#3cff9e] font-extrabold text-lg font-['AudioWide'] tracking-wide cursor-default">{key}</p>
                                        <a href={boxInfo[key][1]} className="text-[#d7e4dd]/60 font-medium font-serif ">{boxInfo[key][0]}</a>
                                    </div>
                                ))
                            }
                            
                        </div>

                        <div className="h-100 w-130 border border-dashed border-[#3cff9e]/40 rounded-3xl flex flex-col p-4 ">
                            
                            <div className="p-2 gap-2">
                                <label className="text-[#3cff9e] font-bold text-sm font-['AudioWide'] tracking-wide cursor-default">Name:</label>
                                <input className="outline-none w-full px-2 py-1 border border-[#3cff9e]/20 rounded-sm text-xs text-[#3cff9e] font-mono" placeholder="Enter Your Name" onChange={(e) => {name.current = e.target.value}}></input>
                            </div>

                            <div className="p-2 gap-2">
                                <label className="text-[#3cff9e] font-bold text-sm font-['AudioWide'] tracking-wide cursor-default">Subject:</label>
                                <input className="outline-none w-full px-2 py-1 border border-[#3cff9e]/20 rounded-sm text-xs text-[#3cff9e] font-mono" 
                                placeholder="Enter the subject of this mail" onChange={(e) => {sbj.current = e.target.value}}></input>
                            </div>

                            <div className="p-2 flex-1 flex flex-col min-h-0 gap-2">
                                <label className="text-[#3cff9e] font-bold text-sm font-['AudioWide'] tracking-wide cursor-default">Message:</label>
                                <textarea className="outline-none w-full flex-1 px-2 py-1 border border-[#3cff9e]/20 resize-none rounded-sm text-xs text-[#3cff9e] font-mono overflow-y-scroll scrollbar-none" 
                                placeholder="Enter the message you want to send." onChange={(e) => {msg.current = e.target.value}}></textarea>
                            </div>
                            
                            <div className = "self-end mt-2">
                                <button className="text-[#3cff9e] font-medium text-sm font-['AudioWide'] tracking-wider border border-[#3cff9e]/30 border-dashed py-1 px-2 rounded-xl" onClick={() => sendMail()}>{"Send >>"}</button>
                            </div>

                        </div>

                    </div>

                </div>

                <MessageBox message={message}></MessageBox>

            </div>
        </>
    )
}

export default ContactPage