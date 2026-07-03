import { useEffect, useState, useRef } from "react"

function MessageBox({ message }) {
    const [queue,   setQueue]   = useState([])
    const [current, setCurrent] = useState(null)
    const [open,    setOpen]    = useState(false)
    const timerRef = useRef(null)

    // ── 1. Enqueue every incoming message ────────────────────────────────────
    // message is always a fresh object reference (or string), so this fires
    // on every new call to setMessage(...) in the parent, even for identical text.
    useEffect(() => {
        if (!message) return
        setQueue(prev => [...prev, message])
    }, [message])

    // ── 2. Dequeue and display whenever the slot is empty ────────────────────
    // Fires when current becomes null (after dismiss finishes) OR when a new
    // item lands in queue while nothing is showing.
    useEffect(() => {
        if (current !== null || queue.length === 0) return
        const [next, ...rest] = queue
        setQueue(rest)
        setCurrent(next)
    }, [current, queue])

    // ── 3. Slide in + start 3-second auto-dismiss whenever current changes ───
    useEffect(() => {
        if (!current) return

        // 10 ms delay lets the element mount first so the CSS transition fires.
        // Without it the element renders already at translate-x-0 with no animation.
        const slideIn = setTimeout(() => setOpen(true), 10)
        timerRef.current = setTimeout(dismiss, 3000)

        return () => {
            clearTimeout(slideIn)
            clearTimeout(timerRef.current)
        }
    }, [current])

    // ── dismiss: slide out → wait for animation → clear current ─────────────
    // Clearing current triggers effect 2 which dequeues the next message if any.
    function dismiss() {
        clearTimeout(timerRef.current)
        setOpen(false)
        setTimeout(() => {
            setCurrent(null)
            setOpen(false)   // reset for the next message's slide-in
        }, 300)              // matches transition-duration-300 in Tailwind
    }

    // Nothing showing and nothing queued — render nothing at all.
    if (!current) return null

    const status = (typeof current === "object" && current !== null) ? current.Status : null
    const text   = (typeof current === "object" && current !== null) ? current.Message : current

    const colors = {
        Success: { border: "border-[#3cff9e]/50", fill: "bg-[#3cff9e]/10", text: "text-[#3cff9e]" },
        Failed:  { border: "border-[#ff4d5e]/50", fill: "bg-[#ff4d5e]/10", text: "text-[#ff4d5e]" },
        Info:    { border: "border-[#4f9df2]/50", fill: "bg-[#4f9df2]/10", text: "text-[#4f9df2]" },
    }
    const c = colors[status] || colors.Info

    return (
        <div className={`
            fixed bottom-4 right-0 z-40 h-20 w-60
            flex items-stretch rounded-l-xl border
            ${c.border} ${c.fill}
            backdrop-blur-sm
            transition-transform duration-300 ease-out
            ${open ? "translate-x-0" : "translate-x-full"}
        `}>

            {/* close button — slides the box back out on click */}
            <button
                type="button"
                className={`w-5 h-full flex items-center justify-center border-r ${c.border} cursor-pointer`}
                onClick={dismiss}
            >
                <span className={`text-sm font-bold ${c.text}`}>{"×"}</span>
            </button>

            {/* message content */}
            <div className="h-auto flex-1 flex flex-col justify-center px-3 py-2 gap-1 overflow-y-scroll scrollbar-none">
                <div className="flex items-center justify-between">
                    {status && (
                        <span className={`text-[11px] font-bold tracking-wide uppercase ${c.text}`}>
                            {status}
                        </span>
                    )}

                    {/* queue depth indicator — lets the user know more are coming */}
                    {queue.length > 0 && (
                        <span className="text-[10px] text-[#d7e4dd]/40">
                            +{queue.length} more
                        </span>
                    )}
                </div>
                <p className="text-xs text-[#d7e4dd]/90 leading-snug line-clamp-3">{text}</p>
            </div>

        </div>
    )
}

export default MessageBox