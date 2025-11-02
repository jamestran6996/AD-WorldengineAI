  import React, { useState } from 'react';
  import { useNavigate } from 'react-router-dom';

  export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
      e.preventDefault();
      setError('');

      try {
        const response = await fetch('http://localhost:8000/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.access_token) {
          localStorage.setItem('token', data.access_token);
          navigate('/dashboard');
        } else {
          setError(data.detail || 'Invalid username or password');
        }
      } catch (err) {
        setError('Cannot connect to server');
      }
    };

    return (
      <div style={{ maxWidth: '400px', margin: 'auto', paddingTop: '50px' }}>
        <h2>Worldengine AI</h2>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '10px' }}>
            <label>Username:</label><br />
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="Username"
                style={{ flex: 1 }}
              />
              <span style={{ marginLeft: '5px', color: '#666' }}>@worldengine.ai</span>
            </div>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Password:</label><br />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: '100%' }}
            />
          </div>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <button type="submit">Log in</button>
        </form>
      </div>
    );
  }
