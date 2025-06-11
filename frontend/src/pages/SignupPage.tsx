import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  AuthContainer,
  AuthBox,
  AuthTitle,
  AuthForm,
  AuthInput,
  AuthButton,
  AuthLink,
} from '../components/auth/AuthStyles';
import { useAuth } from '../contexts/AuthContext';

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const { signup } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      await signup(formData.username, formData.email, formData.password);
      navigate('/chat');
    } catch (err) {
      setError('Failed to create account. Username or email might be taken.');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <AuthContainer>
      <AuthBox
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <AuthTitle>Create Account</AuthTitle>
        <AuthForm onSubmit={handleSubmit}>
          {error && (
            <div style={{ color: '#ff4444', marginBottom: '1rem', textAlign: 'center' }}>
              {error}
            </div>
          )}
          <AuthInput
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            required
          />
          <AuthInput
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <AuthInput
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <AuthInput
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
          <AuthButton
            type="submit"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Sign Up
          </AuthButton>
        </AuthForm>
        <AuthLink>
          Already have an account?{' '}
          <Link to="/login">Login</Link>
        </AuthLink>
      </AuthBox>
    </AuthContainer>
  );
};

export default SignupPage; 