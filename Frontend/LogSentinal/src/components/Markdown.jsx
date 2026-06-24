import Markdown from "react-markdown"

function SummaryPage({
    markdown_str
}){
    return (
        <div className="fixed inset-0 -z-10 bg-[#080c14] font-['Space_Grotesk']" style={{backgroundImage: 'radial-gradient(circle, #d7e4dd22 1px, transparent 1px)', backgroundSize: '24px 24px'}}>
            <div className="top-0 right-0 w-40 h-10">
                <button className="fixed bg-transparent outline-none text-[#d7e4dd]/70">DOWNLOAD</button>
                <Markdown>{markdown_str}</Markdown> 
            </div>
        </div>
    )
}