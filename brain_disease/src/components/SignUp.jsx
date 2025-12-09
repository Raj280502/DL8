import { useState } from "react";
import { useNavigate } from "react-router-dom";

const SignUp = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError("Passwords do not match!");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/api/signup/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        navigate("/home");
      } else {
        setError(data.error || "Signup failed");
      }
    } catch (err) {
      setError("Server error: " + err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ border: "1px solid #ccc" }}>
      <div className="container">
        <h1>Sign Up</h1>
        {error && <p style={{ color: "red" }}>{error}</p>}
        <label><b>Username</b></label>
        <input type="text" placeholder="Enter Username" value={username} onChange={(e)=> setUsername(e.target.value)} required />

        <label><b>Email</b></label>
        <input type="email" placeholder="Enter Email" value={email} onChange={(e)=> setEmail(e.target.value)} required />

        <label><b>Password</b></label>
        <input type="password" placeholder="Enter Password" value={password} onChange={(e)=> setPassword(e.target.value)} required />

        <label><b>Repeat Password</b></label>
        <input type="password" placeholder="Repeat Password" value={confirmPassword} onChange={(e)=> setConfirmPassword(e.target.value)} required />

        <button type="submit" className="signupbtn bg-blue-500 text-white font-bold px-2 rounded">
          Sign Up
        </button>
      </div>
    </form>
  );
};
export default SignUp;
