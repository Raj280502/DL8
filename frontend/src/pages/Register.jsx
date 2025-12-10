import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch('/api/auth/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data?.username?.[0] || data?.email?.[0] || data?.password?.[0] || 'Registration failed');
        return;
      }
      navigate('/login');
    } catch (err) {
      setError('Network error');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <form onSubmit={handleSubmit} className="bg-card p-8 rounded-2xl shadow-lg w-full max-w-md flex flex-col gap-4 border">
        <h2 className="text-2xl font-bold mb-2">Register</h2>
        <input name="username" value={form.username} onChange={handleChange} placeholder="Username" className="input input-bordered" required />
        <input name="email" value={form.email} onChange={handleChange} placeholder="Email" type="email" className="input input-bordered" required />
        <input name="password" value={form.password} onChange={handleChange} placeholder="Password" type="password" className="input input-bordered" required />
        {error && <div className="text-red-500 text-sm">{error}</div>}
        <button type="submit" className="btn-primary py-2 rounded-xl mt-2">Register</button>
        <div className="text-sm mt-2">Already have an account? <a href="/login" className="text-primary underline">Login</a></div>
      </form>
    </div>
  );
}
