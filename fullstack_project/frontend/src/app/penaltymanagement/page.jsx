"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  VStack,
  HStack,
  Button,
  Text,
  createListCollection,
  Center,
} from "@chakra-ui/react";
import {
  SelectContent,
  SelectItem,
  SelectRoot,
  SelectTrigger,
  SelectValueText,
} from "@chakra-ui/react";

const PenaltyManagement = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [selectedUser, setSelectedUser] = useState("");
  const [penaltyType, setPenaltyType] = useState("");
  const [description, setDescription] = useState("");
  const [expiryDate, setExpiryDate] = useState("");
  const [userPenalties, setUserPenalties] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");

  // Penalty type mappings from backend
  const PENALTY_TYPES = {
    0: "Temporary Ban",
    1: "Deactivated",
    2: "Limited Actions",
    3: "Permanent Ban",
  };

  const PENALTY_TYPE_DESCRIPTIONS = {
    0: "User will be temporarily banned from library access",
    1: "User account will be deactivated",
    2: "User will have restricted library access privileges",
    3: "User will be permanently banned from the library",
  };

  // Fetch all users on component mount
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const headers = token ? { Authorization: `Bearer ${token}` } : {};

        const response = await fetch("http://localhost:8000/users/all", {
          headers,
        });

        if (response.ok) {
          const users = await response.json();
          setAllUsers(Array.isArray(users) ? users : []);
        } else {
          setAllUsers([]);
        }
      } catch (error) {
        console.error("Error fetching users:", error);
        setAllUsers([]);
      }
    };

    fetchUsers();
  }, []);

  // Fetch user penalties when user is selected
  useEffect(() => {
    if (selectedUser) {
      fetchUserPenalties();
    } else {
      setUserPenalties([]);
    }
  }, [selectedUser]);

  const fetchUserPenalties = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const response = await fetch(
        `http://localhost:8000/library/penaltyof/${selectedUser}`,
        { headers }
      );

      if (response.ok) {
        const penalties = await response.json();
        setUserPenalties(Array.isArray(penalties) ? penalties : []);
      }
    } catch (error) {
      console.error("Error fetching penalties:", error);
      setUserPenalties([]);
    }
  };

  const handleAddPenalty = async (e) => {
    e.preventDefault();

    if (!selectedUser || !penaltyType || !description) {
      setMessage("Please fill in all required fields");
      setMessageType("error");
      return;
    }

    if (!expiryDate) {
      setMessage("Please set an expiry date");
      setMessageType("error");
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem("access_token");
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const response = await fetch("http://localhost:8000/library/createpenalty", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...headers,
        },
        body: JSON.stringify({
          userid: selectedUser,
          penalty_type: parseInt(penaltyType),
          description: description,
          expiry_date: expiryDate,
          timestamp: new Date().toISOString(),
        }),
      });

      if (response.ok) {
        setMessage("Penalty created successfully!");
        setMessageType("success");
        setPenaltyType("");
        setDescription("");
        setExpiryDate("");
        fetchUserPenalties(); // Refresh penalties list
        setTimeout(() => setMessage(""), 3000);
      } else {
        const error = await response.json();
        setMessage(error.detail || "Failed to create penalty");
        setMessageType("error");
      }
    } catch (error) {
      console.error("Error creating penalty:", error);
      setMessage("Error creating penalty: " + error.message);
      setMessageType("error");
    } finally {
      setLoading(false);
    }
  };

  const filteredUsers = allUsers.filter(
    (user) =>
      (user.userid || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
      (user.email || "").toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Center w="100%" minH="100vh">
      <VStack>
      <VStack maxW="900px" align="start" p={20} mb={-14}>
        <Text fontWeight="bold" fontSize="2xl">
          Penalty Management
        </Text>
        {selectedUser && (
          <VStack alignItems="start" w="100%">
            <Text color="gray.400" fontSize="sm" fontWeight="500">
              Selected User
            </Text>
            <HStack spacing={3} alignItems="center">
              <Button
                variant="outline"
                borderColor="gray.500"
                color="gray.300"
                fontWeight="600"
                fontSize="md"
                px={8}
                h="48px"
                minW="350px"
                justifyContent="flex-start"
                _hover={{ bg: "gray.900", borderColor: "gray.400" }}
              >
                {selectedUser}
              </Button>
              <Button
                bg="white"
                color="gray.900"
                fontWeight="600"
                fontSize="md"
                px={8}
                h="48px"
                _hover={{ bg: "gray.100" }}
                onClick={() => {
                  setSelectedUser("");
                  setUserPenalties([]);
                }}
              >
                Clear
              </Button>
            </HStack>
          </VStack>
        )}
      </VStack>

      {/* Main Content - Two Column Layout */}
      <Box w="100%">
        <Text fontWeight="bold" fontSize={20} mb={5}>
          Add Penalty
        </Text>

        <VStack as="form" onSubmit={handleAddPenalty} spacing={4} w="100%" maxW="500px" mb={12}>
          <Box w="100%">
            <Text mb={2} fontWeight="600" fontSize="sm">
              Select User
            </Text>
            <input
              type="text"
              placeholder="Search by User ID or Email"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                marginBottom: "8px",
                fontFamily: "inherit",
                fontSize: "16px",
                color: "#374151",
              }}
            />

            {searchQuery && filteredUsers.length > 0 && (
              <Box
                maxH="250px"
                overflowY="auto"
                border="2px solid #60a5fa"
                borderRadius="4px"
                bg="linear-gradient(180deg, #f0f9ff 0%, #e0f2fe 100%)"
                position="relative"
                zIndex={10}
              >
                {filteredUsers.map((user) => (
                  <Box
                    key={user.userid}
                    p={3}
                    cursor="pointer"
                    _hover={{ bg: "linear-gradient(90deg, #bfdbfe 0%, #93c5fd 100%)" }}
                    borderBottom="1px solid #bfdbfe"
                    onClick={() => {
                      setSelectedUser(user.userid);
                      setSearchQuery("");
                    }}
                    bg={selectedUser === user.userid ? "linear-gradient(90deg, #60a5fa 0%, #3b82f6 100%)" : "transparent"}
                    transition="all 0.2s"
                  >
                    <Text fontWeight="600" color={selectedUser === user.userid ? "white" : "gray.900"}>
                      {user.userid}
                    </Text>
                    <Text color={selectedUser === user.userid ? "blue.100" : "gray.500"} fontSize="sm">
                      {user.email || "No email"}
                    </Text>
                  </Box>
                ))}
              </Box>
            )}
          </Box>

          <Box w="100%">
            <Text mb={2} fontWeight="600" fontSize="sm">
              Penalty Type (Required)
            </Text>
            <select
              value={penaltyType}
              onChange={(e) => setPenaltyType(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                fontFamily: "inherit",
                fontSize: "16px",
                color: "#374151",
                appearance: "none",
                backgroundImage: "none",
                backgroundColor: "transparent",
              }}
            >
              <option value="" style={{ color: "#9ca3af", opacity: 0.6 }}>Select a penalty type...</option>
              <option value="0" style={{ color: "#374151" }}>Temporary Ban</option>
              <option value="1" style={{ color: "#374151" }}>Deactivated</option>
              <option value="2" style={{ color: "#374151" }}>Limited Actions</option>
              <option value="3" style={{ color: "#374151" }}>Permanent Ban</option>
            </select>
            {penaltyType && (
              <Text fontSize="xs" color="gray.500" mt={1}>
                {PENALTY_TYPE_DESCRIPTIONS[parseInt(penaltyType)]}
              </Text>
            )}
          </Box>

          <Box w="100%">
            <Text mb={2} fontWeight="600" fontSize="sm">
              Description (Required)
            </Text>
            <textarea
              placeholder="Reason and details for this penalty"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              style={{
                width: "100%",
                padding: "8px 12px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                fontFamily: "inherit",
                fontSize: "16px",
                minHeight: "80px",
                resize: "vertical",
                color: "#374151",
              }}
            />
            <style>{`textarea::placeholder { color: #9ca3af; }`}</style>
          </Box>

          <Box w="100%">
            <Text mb={2} fontWeight="600" fontSize="sm">
              Expiry Date (Required)
            </Text>
            <input
              type="datetime-local"
              placeholder="Select date and time"
              value={expiryDate}
              onChange={(e) => setExpiryDate(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                fontFamily: "inherit",
                fontSize: "16px",
                color: "#374151",
              }}
            />
            <style>{`input[type="datetime-local"]::placeholder { color: #9ca3af; }`}</style>
          </Box>

          {message && (
            <Box
              w="100%"
              p={3}
              borderRadius="4px"
              bg={messageType === "success" ? "green.50" : "red.50"}
              border={`1px solid ${messageType === "success" ? "#10b981" : "#ef4444"}`}
            >
              <Text color={messageType === "success" ? "green.600" : "red.600"} fontWeight="600" fontSize="sm">
                {message}
              </Text>
            </Box>
          )}

          <Button
            type="submit"
            w="100%"
            isLoading={loading}
            disabled={!selectedUser || !penaltyType || !description || !expiryDate}
            colorPalette="blue"
            mt={8}
          >
            Create Penalty
          </Button>
        </VStack>
      </Box>

      {/* User Penalties Table */}
      {selectedUser && (
        <Box w="100%" mt={20}>
          <Text fontWeight="bold" fontSize={20} mb={6}>
            Penalties for {selectedUser}
          </Text>

          {userPenalties.length > 0 ? (
            <VStack w="100%" spacing={4} align="stretch">
              <Box w="100%" overflowX="auto" borderRadius="6px" boxShadow="0 2px 8px rgba(59, 130, 246, 0.15)">
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid #60a5fa", backgroundColor: "#dbeafe" }}>
                      <th style={{ padding: "14px", textAlign: "left", fontWeight: "700", color: "#1e40af", fontSize: "14px" }}>Penalty Type</th>
                      <th style={{ padding: "14px", textAlign: "left", fontWeight: "700", color: "#1e40af", fontSize: "14px" }}>Description</th>
                      <th style={{ padding: "14px", textAlign: "left", fontWeight: "700", color: "#1e40af", fontSize: "14px" }}>Created</th>
                      <th style={{ padding: "14px", textAlign: "left", fontWeight: "700", color: "#1e40af", fontSize: "14px" }}>Expires</th>
                      <th style={{ padding: "14px", textAlign: "left", fontWeight: "700", color: "#1e40af", fontSize: "14px" }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {userPenalties.map((penalty, idx) => (
                      <tr key={penalty.penalty_id || idx} style={{ borderBottom: idx === userPenalties.length - 1 ? "2px solid #60a5fa" : "1px solid #bfdbfe", backgroundColor: idx % 2 === 0 ? "#f0f9ff" : "white" }}>
                        <td style={{ padding: "14px", color: "#1e40af", fontWeight: "700" }}>
                          {PENALTY_TYPES[penalty.penalty_type] || `Type ${penalty.penalty_type}`}
                        </td>
                        <td style={{ padding: "14px", color: "#374151", maxWidth: "300px" }}>
                          {penalty.description || "N/A"}
                        </td>
                        <td style={{ padding: "14px", color: "#374151", fontSize: "sm" }}>
                          {penalty.timestamp ? new Date(penalty.timestamp).toLocaleDateString() : "N/A"}
                        </td>
                        <td style={{ padding: "14px", color: "#374151", fontSize: "sm" }}>
                          {penalty.expiry_date ? new Date(penalty.expiry_date).toLocaleDateString() : "N/A"}
                        </td>
                        <td style={{ padding: "12px" }}>
                          <span style={{
                            padding: "4px 12px",
                            borderRadius: "9999px",
                            fontSize: "14px",
                            fontWeight: "600",
                            backgroundColor: penalty.active ? "#fee2e2" : "#dcfce7",
                            color: penalty.active ? "#dc2626" : "#16a34a",
                            display: "inline-block"
                          }}>
                            {penalty.active ? "Active" : "Expired"}
                          </span>
                        </td>
                      </tr>
                    ))}
                    <tr style={{ backgroundColor: "#dbeafe", fontWeight: "700" }}>
                      <td style={{ padding: "14px", color: "#1e40af", fontWeight: "700", borderTop: "2px solid #60a5fa" }}>
                        Total Penalties: {userPenalties.length}
                      </td>
                      <td colSpan="4" style={{ padding: "14px", borderTop: "2px solid #60a5fa" }}></td>
                    </tr>
                  </tbody>
                </table>
              </Box>
            </VStack>
          ) : (
            <Box
              p={6}
              bg="gray.50"
              borderRadius="4px"
              textAlign="center"
              border="1px solid #e5e7eb"
            >
              <Text color="gray.500" fontSize="sm">
                No penalties for this user
              </Text>
            </Box>
          )}
        </Box>
      )}
      </VStack>
    </Center>
  );
};

export default PenaltyManagement;
