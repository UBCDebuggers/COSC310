"use client"
import React from 'react';
import { useRouter } from "next/navigation";
import { Box, Heading, Text } from "@chakra-ui/react";

const AdminPage = () => {
  const router = useRouter();
  
  React.useEffect(() => {
    // ✅ Only run this after component mounts
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      console.log("Access token:", token);  // 👈 Add this

      if (!token) {
        router.push("/Admin"); // redirect if not logged in
      }
    }
  }, [router]);


 return (
    <Box p={10} bg="white" color="blue.700" minH="100vh">
      <Heading color="blue.800" mb={4}>
        Welcome to your admin dashboard 
      </Heading>
      <Text fontSize="lg" color="blue.600">
        You’re successfully logged in! <strong>"WE DID IT LADS!!!, Boys, Run it fam"</strong> – Hakim & Ahab
      </Text>
    </Box>
  );
}

export default AdminPage;