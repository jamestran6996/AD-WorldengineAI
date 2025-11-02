import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function AdminPage() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');

    if (!token) {
      navigate('/login');
      return;
    }

    fetch('http://localhost:8000/protected', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then(async (res) => {
        if (res.ok) {
          const data = await res.json();
          if (data.role !== 'admin') {
            navigate('/dashboard');
          } else {
            setUser(data);
          }
        } else {
          localStorage.removeItem('token');
          navigate('/login');
        }
      })
      .catch(() => {
        setError('Cannot connect to server');
      });
  }, [navigate]);

  if (error) {
    return <p style={{ color: 'red' }}>{error}</p>;
  }

  if (!user) {
    return <p>Loading...</p>;
  }

  return (
    <div style={{ maxWidth: '600px', margin: 'auto', paddingTop: '50px' }}>
      <h2>🔐 Admin</h2>
      <p>Welcome Admin <strong>{user.username}</strong>!</p>

      <div style={{ marginTop: '20px' }}>
        <h3>Function:</h3>
        <ul>
          <li>function 1</li>
          <li>function 2</li>
          <li>function 3</li>
          {/* add later */}
        </ul>
      </div>

      <button
        style={{ marginTop: '30px' }}
        onClick={() => {
          localStorage.removeItem('token');
          navigate('/login');
        }}
      >
        Log out
      </button>
    </div>
  );
}
