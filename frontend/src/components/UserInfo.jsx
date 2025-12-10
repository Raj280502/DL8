
import { User as UserIcon, Mail } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function UserInfo() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access');
    if (!token) return;
    fetch('/api/auth/user/', {
      headers: { 'Authorization': `Bearer ${token}` },
    })
      .then(res => res.ok ? res.json() : Promise.reject(res))
      .then(data => setUser(data))
      .catch(() => setError('Could not fetch user info'));
  }, []);

  if (!user) return error ? <div className="text-red-500">{error}</div> : null;

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2 mb-1">
        <span className="rounded-full bg-primary/10 p-2"><UserIcon className="h-5 w-5 text-primary" /></span>
        <span className="font-semibold text-foreground text-base">{user.username}</span>
      </div>
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Mail className="h-4 w-4" />
        <span>{user.email}</span>
      </div>
    </div>
  );
}
