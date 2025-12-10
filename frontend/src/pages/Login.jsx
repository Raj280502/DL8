import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data?.error || 'Login failed');
        return;
      }
      localStorage.setItem('access', data.access);
      localStorage.setItem('refresh', data.refresh);
      navigate('/');
    } catch (err) {
      setError('Network error');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <form onSubmit={handleSubmit} className="bg-card p-8 rounded-2xl shadow-lg w-full max-w-md flex flex-col gap-4 border">
        <h2 className="text-2xl font-bold mb-2">Login</h2>
        <input name="username" value={form.username} onChange={handleChange} placeholder="Username" className="input input-bordered" required />
        <input name="password" value={form.password} onChange={handleChange} placeholder="Password" type="password" className="input input-bordered" required />
        {error && <div className="text-red-500 text-sm">{error}</div>}
        <button type="submit" className="btn-primary py-2 rounded-xl mt-2">Login</button>
        <div className="text-sm mt-2">Don't have an account? <a href="/register" className="text-primary underline">Register</a></div>
      </form>
    </div>
  );
}
