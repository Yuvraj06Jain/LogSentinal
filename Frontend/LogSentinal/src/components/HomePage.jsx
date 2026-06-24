function Home({
  setHome
}){
  return(
    <div className="fixed inset-0 -z-10 bg-[#080c14] tracking-widest font-['Audiowide']" style={{backgroundImage: 'radial-gradient(circle, #d7e4dd22 1px, transparent 1px)', backgroundSize: '24px 24px'}}>
      <div className="min-h-screen flex flex-col items-center justify-center gap-5 text-center">
        <button className="font-extrabold text-9xl cursor-pointer text-[#3cff9e] active:text-[#d7e4dd]/40 duration-100 " onClick = {() => {
          setHome(false)
          }}>
          LogSentinal</button>
        <p className="font-extrabold text-xl cursor-default text-[#d7e4dd]/60 tracking-wide">Monitor your logs, Catch Threats before they catch you.</p>
      </div>
    </div>
  )
}

export default Home;