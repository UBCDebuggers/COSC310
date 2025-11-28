import React from "react";
import { Box, Text } from "@chakra-ui/react";

const StudentPage = () => {
  return (
    <Box
      p={10}
      bg="white"
      color="blue.700"
      minH="100vh"
      display="flex"
    
    >
      <Text fontSize="2xl" fontWeight="bold" color="blue.800">
       Welcome to your Student Dashboard
      </Text>
    </Box>
  );
};

export default StudentPage;
