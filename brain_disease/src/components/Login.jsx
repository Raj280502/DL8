import { useState } from "react";
import { useNavigate } from "react-router-dom";
const Login = () => {
    const navigate = useNavigate();
    const [uname, setUname] = useState("");
    const [psw, setPsw] = useState("");
    const handleSubmit =(e)=>{
        e.preventDefault();
        console.log(uname, psw);
         if (uname  && psw) {
        navigate('/home');
    }
    };

   
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleSubmit}>
        <div className="container">
          <label htmlFor="uname">
            <b>Username</b>
          </label>
          <input
            type="text"
            placeholder="Enter Username"
            name="uname"
            value={uname}
            onChange={(e) => setUname(e.target.value)}
            required
          />

          <label htmlFor="psw">
            <b>Password</b>
          </label>
          <input
            type="password"
            placeholder="Enter Password"
            name="psw"
            value={psw}
            onChange={(e) => setPsw(e.target.value)}
            required
          />

          <button className="bg-blue-500 text-white font-bold  px-2 rounded" type="submit">Login</button>
          <span> don't have account ? <a href="/register">Register</a></span>
        </div>
      </form>
    </div>
  );
};
export default Login;
