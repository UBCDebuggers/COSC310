"use client"
import { createContext, useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const router = useRouter();

    const login = async (username, password) => {
        try {
            const params = new URLSearchParams();

            params.append('username', username);
            params.append('password', password);

            const response = await axios.post('http://localhost:8000/auth/login', params, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded'},
            });
            axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
            localStorage.setItem('access_token', response.data.access_token);
            setUser(response.data.user);
            
            const token = response.data.access_token;
            const payload = JSON.parse(atob(token.split('.')[1]));
            const isAdmin = payload.admin || false;
            
            console.log("Token payload:", payload);
            console.log("Is admin:", isAdmin);
            
            router.push(isAdmin ? '/admindashboard' : '/dashboard');
        } catch (error) {
            console.error("Login failed:", error);
            if (error.response) {
                console.error("Response status:", error.response.status);
                console.error("Response data:", error.response.data);
            } else if (error.request) {
                console.error("No response received:", error.request);
            } else {
                console.error("Error message:", error.message);
            }
        }
    };

    const logout = () => {
        setUser(null);
        delete axios.defaults.headers.common['Authorization'];
        localStorage.removeItem('access_token');
        router.push('/login');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export default AuthContext;