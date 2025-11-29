"use client";
import React from "react";
import { useRouter } from "next/navigation";
import { Box, Heading, Text } from "@chakra-ui/react";

const page = () => {
  const router = useRouter();

  React.useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      //router.push("/");
    }
  }, [router]);

  return (
    <Box p={10}>
      <Heading>Welcome to your Dashboard 🎉</Heading>
      <Text mt={4}>
        You’re successfully logged in! "WE DID IT LADS!!!" - Hakim
      </Text>
    </Box>
  );
};

export default page;
