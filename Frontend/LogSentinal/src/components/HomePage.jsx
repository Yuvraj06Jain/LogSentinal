function Home({
  setHome
}){
  return(
    <div className="fixed inset-0 -z-10 bg-slate-950" style={{backgroundImage: 'radial-gradient(circle, #ffffff22 1px, transparent 1px)', backgroundSize: '24px 24px'}}>
      <div className="min-h-screen flex flex-col items-center justify-center gap-5 text-center">
        <button className="font-extrabold text-9xl cursor-pointer text-cyan-500 active:text-slate-500 duration-100 " onClick = {() => {
          setHome(false)
          }}>
          LogSentinal</button>
        <p className="font-extrabold text-xl cursor-default text-slate-400 tracking-wide">Monitor your logs, Catch Threats before they catch you.</p>
      </div>
    </div>
  )
}

export default Home;