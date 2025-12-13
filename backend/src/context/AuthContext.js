import React, { createContext, useState, useEffect } from 'react';
import { jwtDecode } from "jwt-decode";
import api from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const decoded = jwtDecode(token);
                // Check if token is expired
                if (decoded.exp * 1000 < Date.now()) {
                    localStorage.removeItem('token');
                    setUser(null);
                } else {
                    setUser(decoded);
                }
            } catch (error) {
                console.error("Token decode error:", error);
                localStorage.removeItem('token');
            }
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        try {
            const response = await api.post('/auth/login', { email, password });
            const { token, user: userData } = response.data;
            
            // Token'ı kaydet
            localStorage.setItem('token', token);
            
            // Decode token to get full user info
            const decoded = jwtDecode(token);
            setUser({ ...decoded, ...userData }); // Merge token data with user data
            
            return { success: true };
        } catch (error) {
            console.error("Login error:", error);
            return { 
                success: false, 
                error: error.response?.data?.error || "Login failed" 
            };
        }
    };

    const register = async (email, password, fullName) => {
        try {
            const response = await api.post('/auth/register', { 
                email, 
                password, 
                full_name: fullName 
            });
            const { token, user: userData } = response.data;
            
            localStorage.setItem('token', token);
            
            const decoded = jwtDecode(token);
            setUser({ ...decoded, ...userData });
            
            return { success: true };
        } catch (error) {
            console.error("Register error:", error);
            return { 
                success: false, 
                error: error.response?.data?.error || "Registration failed" 
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};