"use client"

import { useContext, useEffect } from "react"
import { useRouter } from "next/navigation"
import AuthContext from "@/app/context/AuthContext"

const ProtectedRoute = ({ children }) => {
    const { user } = useContext(AuthContext);
    const router = useRouter();

    useEffect(() => {
        if (!user) {
            router.push('/login');
        }
    }, [user, router]);

    return user ? children : null;
    
}