"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Box, Text, VStack, HStack, Button, FileUpload, Center, Input } from "@chakra-ui/react";
import { HiUpload } from "react-icons/hi";
import { Chart, useChart } from "@chakra-ui/charts"
import { Area, AreaChart, BarChart, Bar, Line, LineChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts"

const transformLoansByDate = (loans) => {
  if (!Array.isArray(loans)) return [];
  const dateMap = {};
  loans.forEach(loan => {
    const date = new Date(loan.expiry_date).toLocaleDateString();
    dateMap[date] = (dateMap[date] || 0) + 1;
  });
  return Object.entries(dateMap).map(([date, count]) => ({ date, count }));
};

const transformOverdueTrend = (loans) => {
  if (!Array.isArray(loans)) return [];
  const today = new Date();
  const overdueMap = {};
  loans.forEach(loan => {
    const expiry = new Date(loan.expiry_date);
    if (expiry < today) {
      const date = expiry.toLocaleDateString();
      overdueMap[date] = (overdueMap[date] || 0) + 1;
    }
  });
  return Object.entries(overdueMap).map(([date, count]) => ({ date, count }));
};

const transformMostBorrowed = (loans) => {
  if (!Array.isArray(loans)) return [];
  const isbnMap = {};
  loans.forEach(loan => {
    if (!isbnMap[loan.isbn]) {
      isbnMap[loan.isbn] = { count: 0, userid: loan.userid };
    }
    isbnMap[loan.isbn].count += 1;
  });
  return Object.entries(isbnMap)
    .sort(([, a], [, b]) => b.count - a.count)
    .slice(0, 10)
    .map(([isbn, data]) => ({ isbn, count: data.count, userid: data.userid }));
};

const transformUserDistribution = (loans) => {
  if (!Array.isArray(loans)) return [];
  const userMap = {};
  loans.forEach(loan => {
    userMap[loan.userid] = (userMap[loan.userid] || 0) + 1;
  });
  return Object.entries(userMap).map(([userid, count]) => ({ userid, count }));
};

const transformPenaltiesByUser = (penalties) => {
  if (!Array.isArray(penalties)) return [];
  return penalties.map(p => ({
    userid: p.userid,
    penalty: p.penalty_amount || 0,
  }));
};

const parseCSVData = (text) => {
  const lines = text.split('\n').filter(line => line.trim());
  if (lines.length === 0) return [];
  
  const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
  return lines.slice(1).map(line => {
    const values = line.split(',').map(v => v.trim());
    const obj = {};
    headers.forEach((header, i) => {
      obj[header] = isNaN(values[i]) ? values[i] : parseFloat(values[i]);
    });
    return obj;
  });
};

const adminpage = () => {
  const router = useRouter();
  
  // Color palette that works in both light and dark modes using Chakra's token system
  const colors = {
    containerBg: { base: "white", _dark: "#0f1419" },
    containerBorder: { base: "gray.200", _dark: "#2d3748" },
    inputBg: { base: "gray.50", _dark: "#2d3748" },
    inputBorder: { base: "gray.300", _dark: "#4a5568" },
    inputText: { base: "gray.900", _dark: "#e2e8f0" },
    labelText: { base: "gray.600", _dark: "gray.300" },
    placeholderText: { base: "gray.400", _dark: "#708090" },
    buttonText: { base: "gray.600", _dark: "#a0aec0" },
    buttonTextHover: { base: "gray.700", _dark: "#cbd5e0" },
    headerText: { base: "gray.900", _dark: "white" },
    subheaderText: { base: "gray.700", _dark: "gray.200" }
  };
  const [topPicks, setTopPicks] = useState([]);
  const [popularBooks, setPopularBooks] = useState([]);
  const [engagingBooks, setEngagingBooks] = useState([]);
  const [userLoans, setUserLoans] = useState([]);
  const [outstandingLoans, setOutstandingLoans] = useState([]);
  const [penalties, setPenalties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [loansChartData, setLoansChartData] = useState([]);
  const [overdueChartData, setOverdueChartData] = useState([]);
  const [mostBorrowedData, setMostBorrowedData] = useState([]);
  const [userDistData, setUserDistData] = useState([]);
  const [penaltyChartData, setPenaltyChartData] = useState([]);
  const [analyticsData, setAnalyticsData] = useState([]);
  const [trendingBooks, setTrendingBooks] = useState([]);
  const [useUploadedData, setUseUploadedData] = useState(false);
  const [uploadedLoans, setUploadedLoans] = useState([]);
  const [uploadedPenalties, setUploadedPenalties] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [filterUser, setFilterUser] = useState("");
  const [loansUploadedFile, setLoansUploadedFile] = useState(null);
  const [loansUploadedData, setLoansUploadedData] = useState([]);
  const [checkoutUserid, setCheckoutUserid] = useState("");
  const [checkoutIsbn, setCheckoutIsbn] = useState("");
  const [checkoutStatus, setCheckoutStatus] = useState("");
  const [checkoutMessage, setCheckoutMessage] = useState("");
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [pendingCheckouts, setPendingCheckouts] = useState([]);
  const [confirmedCheckouts, setConfirmedCheckouts] = useState([]);

  // Load saved state from localStorage on mount
  useEffect(() => {
    try {
      const savedState = localStorage.getItem('adminDashboardState');
      if (savedState) {
        const state = JSON.parse(savedState);
        setOutstandingLoans(state.outstandingLoans || []);
        setPenalties(state.penalties || []);
        setUserLoans(state.userLoans || []);
        setLoansChartData(state.loansChartData || []);
        setOverdueChartData(state.overdueChartData || []);
        setMostBorrowedData(state.mostBorrowedData || []);
        setUserDistData(state.userDistData || []);
        setPenaltyChartData(state.penaltyChartData || []);
      }
    } catch (error) {
      console.log("No saved state found or error loading state:", error);
    }
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('access_token');
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
        
        let userInfo = null;
        let isAdmin = false;
        if (token) {
          try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            userInfo = payload;
            isAdmin = payload.is_admin || payload.admin || false;
            console.log("Admin status:", isAdmin, "User info:", userInfo);
          } catch (e) {
            console.error("Token decode failed:", e);
            // Token decode failed, continue without user info
          }
        }

        const [items, popularItems, engagingItems, userItems, outstandingItems, penaltyItems, analyticsItems, trendingItems] = await Promise.all([
          fetch("http://localhost:8000/recommend/toprated/5").then((r) => r.json()).catch(() => []),
          fetch("http://localhost:8000/recommend/popular/10").then((r) => r.json()).catch(() => []),
          fetch("http://localhost:8000/recommend/topengagement/10").then((r) => r.json()).catch(() => []),
          isAdmin ? fetch("http://localhost:8000/library/userloans?userid=" + encodeURIComponent(userInfo?.sub || ""), { headers }).then((r) => r.ok ? r.json() : []).catch(() => []) : Promise.resolve([]),
          isAdmin ? fetch("http://localhost:8000/library/outstandingloans", { headers }).then((r) => r.ok ? r.json() : []).catch(() => []) : Promise.resolve([]),
          isAdmin ? fetch("http://localhost:8000/library/activepenalties", { headers }).then((r) => r.ok ? r.json() : []).catch(() => []) : Promise.resolve([]),
          isAdmin ? fetch("http://localhost:8000/analytics?limit=1000", { headers }).then((r) => r.ok ? r.json() : []).catch(() => []) : Promise.resolve([]),
          isAdmin ? fetch("http://localhost:8000/analytics/trending?n=10", { headers }).then((r) => r.ok ? r.json() : []).catch(() => []) : Promise.resolve([]),
        ]);
        
        const [booksTop, booksPopular, booksEngaging] = await Promise.all([
          Promise.all(
            (items || []).map((item) =>
              fetch(`http://localhost:8000/books/${encodeURIComponent(item.isbn)}`)
                .then((res) => res.json())
                .catch(() => ({}))
            )
          ),
          Promise.all(
            (popularItems || []).map((item) =>
              fetch(`http://localhost:8000/books/${encodeURIComponent(item.isbn)}`)
                .then((res) => res.json())
                .catch(() => ({}))
            )
          ),
          Promise.all(
            (engagingItems || []).map((item) =>
              fetch(`http://localhost:8000/books/${encodeURIComponent(item.isbn)}`)
                .then((res) => res.json())
                .catch(() => ({}))
            )
          ),
        ]);

        setTopPicks(booksTop.filter(b => b && Object.keys(b).length > 0));
        setPopularBooks(booksPopular.filter(b => b && Object.keys(b).length > 0));
        setEngagingBooks(booksEngaging.filter(b => b && Object.keys(b).length > 0));

        setUserLoans(userItems || []);
        setOutstandingLoans(outstandingItems || []);
        setPenalties(penaltyItems || []);
        setAnalyticsData(analyticsItems || []);
        setTrendingBooks(trendingItems || []);

        // Debug logging
        console.log("Fetched data:", {
          outstandingLoans: outstandingItems?.length || 0,
          penalties: penaltyItems?.length || 0,
          analytics: analyticsItems?.length || 0,
          trending: trendingItems?.length || 0,
          userLoans: userItems?.length || 0
        });

        // Transform analytics data for most borrowed books chart
        if (analyticsItems && analyticsItems.length > 0) {
          // Aggregate request_count by book_id from analytics
          const bookRequestMap = {};
          analyticsItems.forEach(record => {
            const bookId = record.book_id || record.isbn;
            const requestCount = parseInt(record.request_count || 0);
            if (bookId) {
              if (!bookRequestMap[bookId]) {
                bookRequestMap[bookId] = {
                  isbn: bookId,
                  count: 0,
                  title: record.title || bookId
                };
              }
              bookRequestMap[bookId].count += requestCount;
            }
          });
          
          // Convert to array and sort by count, take top 10
          const mostBorrowedFromAnalytics = Object.values(bookRequestMap)
            .sort((a, b) => b.count - a.count)
            .slice(0, 10);
          
          console.log("Most borrowed from analytics:", mostBorrowedFromAnalytics);
          
          // If we have analytics data, use it; otherwise fall back to loan-based data
          if (mostBorrowedFromAnalytics.length > 0) {
            setMostBorrowedData(mostBorrowedFromAnalytics);
          }
        }

        // Populate pending checkouts from outstanding loans with book titles
        if (outstandingItems && outstandingItems.length > 0) {
          const pendingWithTitles = await Promise.all(
            outstandingItems.map(async (loan) => {
              try {
                const bookRes = await fetch(`http://localhost:8000/books/${encodeURIComponent(loan.isbn)}`);
                const bookData = bookRes.ok ? await bookRes.json() : {};
                return {
                  userid: loan.userid,
                  isbn: loan.isbn,
                  title: bookData.title || "Unknown Title",
                  timestamp: new Date(loan.reservation_date).toLocaleString(),
                };
              } catch (e) {
                return {
                  userid: loan.userid,
                  isbn: loan.isbn,
                  title: "Unknown Title",
                  timestamp: new Date(loan.reservation_date).toLocaleString(),
                };
              }
            })
          );
          setPendingCheckouts(pendingWithTitles);
        }

        // Only update chart data if API returned actual data
        if (outstandingItems && outstandingItems.length > 0) {
          const loansData = transformLoansByDate(outstandingItems);
          const overdueData = transformOverdueTrend(outstandingItems);
          console.log("Loans chart data:", loansData);
          console.log("Overdue chart data:", overdueData);
          
          setLoansChartData(loansData);
          setOverdueChartData(overdueData);
          
          // Only use loan-based most borrowed if analytics didn't provide data
          if (!analyticsItems || analyticsItems.length === 0) {
            const mostBorrowedFromLoans = transformMostBorrowed(outstandingItems);
            console.log("Most borrowed from loans (fallback):", mostBorrowedFromLoans);
            setMostBorrowedData(mostBorrowedFromLoans);
          }
        }
        if (userItems && userItems.length > 0) {
          const userDist = transformUserDistribution(userItems);
          console.log("User distribution data:", userDist);
          setUserDistData(userDist);
        }
        if (penaltyItems && penaltyItems.length > 0) {
          const penaltyData = transformPenaltiesByUser(penaltyItems);
          console.log("Penalty chart data:", penaltyData);
          setPenaltyChartData(penaltyData);
        }

        // Save state to localStorage for persistence
        const dashboardState = {
          outstandingLoans: outstandingItems || [],
          penalties: penaltyItems || [],
          userLoans: userItems || [],
          loansChartData: loansChartData,
          overdueChartData: overdueChartData,
          mostBorrowedData: mostBorrowedData,
          userDistData: userDistData,
          penaltyChartData: penaltyChartData,
          timestamp: new Date().toISOString()
        };
        localStorage.setItem('adminDashboardState', JSON.stringify(dashboardState));

        setLoading(false);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError(error.message);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getFilteredData = () => {
    if (!filterUser || filterUser.trim() === "") {
      return { loans: loansChartData, penalties: penaltyChartData, overdue: overdueChartData };
    }
    return {
      loans: loansChartData.filter(item => item.userid === filterUser),
      penalties: penaltyChartData.filter(item => item.userid === filterUser),
      overdue: overdueChartData.filter(item => item.userid === filterUser)
    };
  };

  const handleLoansFileUpload = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const fileName = file.name.toLowerCase();
    if (!fileName.endsWith('.csv') && !fileName.endsWith('.json')) {
      alert('Please upload a CSV or JSON file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result;
        let parsedData = [];

        if (fileName.endsWith('.json')) {
          parsedData = JSON.parse(content);
        } else {
          parsedData = parseCSVData(content);
        }

        if (!Array.isArray(parsedData) || parsedData.length === 0) {
          alert('No valid data found in file');
          return;
        }

        // Transform the data to match loans chart format (needs date and count)
        const transformedData = transformLoansByDate(parsedData);
        if (transformedData.length > 0) {
          setLoansUploadedData(transformedData);
          setLoansUploadedFile(file.name);
        } else {
          alert('Could not transform data. Ensure CSV/JSON has "expiry_date" field');
        }
      } catch (error) {
        alert('Error parsing file: ' + error.message);
      }
    };
    reader.readAsText(file);
  };

  const resetLoansUpload = () => {
    setLoansUploadedFile(null);
    setLoansUploadedData([]);
    const fileInput = document.getElementById('loansFileInput');
    if (fileInput) fileInput.value = '';
  };

  const handleConfirmCheckout = async () => {
    if (!checkoutUserid.trim() || !checkoutIsbn.trim()) {
      setCheckoutMessage("Please enter both User ID and ISBN");
      return;
    }

    setCheckoutLoading(true);
    setCheckoutMessage("");
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/library/confirmcheckout?userid=${encodeURIComponent(checkoutUserid)}&isbn=${encodeURIComponent(checkoutIsbn)}&status_code_val=${checkoutStatus}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        setCheckoutMessage(`Error: ${errorData.detail || 'Failed to confirm checkout'}`);
      } else {
        const data = await response.json();
        setCheckoutMessage(`Success! ${data.message}`);
        
        // Find the pending checkout that was just confirmed
        const confirmedCheckout = pendingCheckouts.find(
          c => c.userid === checkoutUserid && c.isbn === checkoutIsbn
        );
        
        // Remove from pending checkouts
        if (confirmedCheckout) {
          setPendingCheckouts(pendingCheckouts.filter(
            c => !(c.userid === checkoutUserid && c.isbn === checkoutIsbn)
          ));
          
          // Add to confirmed checkouts with the selected status
          const statusLabel = ["Not Returned", "Returned", "Returned Overdue", "Not Returned Overdue", "Cancelled"][checkoutStatus];
          const newConfirmation = {
            userid: checkoutUserid,
            isbn: checkoutIsbn,
            title: confirmedCheckout.title,
            status: statusLabel,
            timestamp: new Date().toLocaleString()
          };
          setConfirmedCheckouts([newConfirmation, ...confirmedCheckouts]);
        }
        
        // Clear form
        setCheckoutUserid("");
        setCheckoutIsbn("");
        setCheckoutStatus(0);
      }
    } catch (error) {
      setCheckoutMessage(`Error: ${error.message}`);
    } finally {
      setCheckoutLoading(false);
    }
  };

  const getLoansChartData = () => {
    if (loansUploadedData.length > 0) {
      return loansUploadedData;
    }
    return getFilteredData().loans;
  };

  const loansChart = useChart({
    data: getLoansChartData().length > 0 ? getLoansChartData() : [],
    series: [{ name: "count", color: "blue.solid" }],
  });

  const overdueChart = useChart({
    data: getFilteredData().overdue.length > 0 ? getFilteredData().overdue : [],
    series: [{ name: "count", color: "red.solid" }],
  });

  const borrowedChart = useChart({
    data: filterUser && mostBorrowedData.length > 0
      ? mostBorrowedData.filter(item => item.userid === filterUser)
      : (mostBorrowedData.length > 0 ? mostBorrowedData : []),
    series: [{ name: "count", color: "green.solid" }],
  });

  const userChart = useChart({
    data: filterUser && userDistData.length > 0 
      ? userDistData.filter(item => item.userid === filterUser)
      : (userDistData.length > 0 ? userDistData : []),
    series: [{ name: "count", color: "purple.solid" }],
  });

  const penaltyChart = useChart({
    data: filterUser && penaltyChartData.length > 0 
      ? penaltyChartData.filter(item => item.userid === filterUser)
      : (penaltyChartData.length > 0 ? penaltyChartData : []),
    series: [{ name: "penalty", color: "orange.solid" }],
  });

  // Transform trending books data for chart
  const trendingChartData = trendingBooks.map(book => ({
    isbn: book.book_id || book.isbn,
    requests: book.total_requests || 0,
    delta: book.delta_requests || 0,
  }));

  const trendingChart = useChart({
    data: trendingChartData.length > 0 ? trendingChartData : [],
    series: [
      { name: "requests", color: "teal.solid" },
      { name: "delta", color: "purple.solid" },
    ],
  });

  return (
    <VStack w="100%" spacing={8} p={6}>
      <VStack w="100%" align="start" spacing={4} pb={6} borderBottom="1px" borderColor="gray.200">
        <Text fontWeight="bold" fontSize={28}>
          Admin Dashboard
        </Text>
        <HStack w="100%">
          <input type="text" placeholder="Filter by User ID (e.g., user1)" value={filterUser} onChange={(e) => setFilterUser(e.target.value)} style={{ padding: "8px 12px", border: "1px solid #ccc", borderRadius: "4px", minWidth: "250px" }} />
          {filterUser && <Button size="sm" onClick={() => setFilterUser("")}>Clear</Button>}
        </HStack>
      </VStack>

      {error && (
        <Box p={4} bg="red.50" border="1px solid" borderColor="red.200" borderRadius="md">
          <Text color="red.600">Error loading data: {error}</Text>
        </Box>
      )}

      {loading && (
        <Box p={4} textAlign="center">
          <Text>Loading dashboard data...</Text>
        </Box>
      )}

      <Box w="100%">
        <Text fontWeight="bold" fontSize={20} mb={4}>
          Loans by Expiry Date {loansChartData.length > 0 && `(${loansChartData.length} data points)`}
        </Text>
        {loansChartData.length === 0 && !loading && (
          <Box p={4} bg="gray.50" border="1px solid" borderColor="gray.200" borderRadius="md" mb={4}>
            <Text color="gray.600">No loan data available. Charts will populate when there are outstanding loans.</Text>
          </Box>
        )}
        <HStack w="100%" mb={4} spacing={2}>
          <Box position="relative" display="inline-block">
            <input
              id="loansFileInput"
              type="file"
              accept=".csv,.json"
              onChange={handleLoansFileUpload}
              style={{ display: 'none' }}
            />
            <button
              onClick={() => document.getElementById('loansFileInput')?.click()}
              style={{
                padding: "10px 16px",
                border: "1px solid #ccc",
                borderRadius: "4px",
                backgroundColor: "transparent",
                color: "#a0aec0",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
                fontFamily: "inherit",
                fontSize: "16px",
                height: "40px",
                minWidth: "160px"
              }}
            >
              <HiUpload /> Upload CSV/JSON
            </button>
          </Box>
          {loansUploadedFile && (
            <>
              <Box
                border="1px solid #ccc"
                borderRadius="4px"
                bg="transparent"
                h="40px"
                minWidth="160px"
                px="16px"
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <span style={{ fontSize: "16px", color: "#a0aec0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{loansUploadedFile}</span>
              </Box>
              <Button size="sm" h="40px" minW="80px" onClick={resetLoansUpload}>Reset</Button>
            </>
          )}
        </HStack>
        <Chart.Root maxH="sm" chart={loansChart}>
          <AreaChart data={getLoansChartData()}>
            <CartesianGrid stroke={loansChart.color("border")} vertical={false} strokeDasharray="3 3" />
            <XAxis dataKey="date" tickLine={false} axisLine={false} />
            <YAxis tickLine={false} axisLine={false} />
            <Tooltip cursor={false} animationDuration={100} content={<Chart.Tooltip />} />
            <Legend content={<Chart.Legend />} />
            {loansChart.series.map((item) => (
              <defs key={item.name}>
                <Chart.Gradient
                  id={`${item.name}-gradient`}
                  stops={[
                    { offset: "0%", color: item.color, opacity: 0.3 },
                    { offset: "100%", color: item.color, opacity: 0.05 },
                  ]}
                />
              </defs>
            ))}
            {loansChart.series.map((item) => (
              <Area
                key={item.name}
                type="natural"
                isAnimationActive={false}
                dataKey="count"
                fill={`url(#${item.name}-gradient)`}
                stroke={loansChart.color(item.color)}
                strokeWidth={2}
              />
            ))}
          </AreaChart>
        </Chart.Root>
      </Box>

      <HStack w="100%" spacing={4}>
        <Box flex={1}>
          <Text fontWeight="bold" fontSize={20} mb={4}>
            Overdue Loans Trend {overdueChartData.length > 0 && `(${overdueChartData.length} data points)`}
          </Text>
          {overdueChartData.length === 0 && !loading && (
            <Box p={4} bg="gray.50" border="1px solid" borderColor="gray.200" borderRadius="md" mb={4}>
              <Text color="gray.600" fontSize="sm">No overdue loans data available.</Text>
            </Box>
          )}
          <Chart.Root maxH="lg" chart={overdueChart}>
            <LineChart data={overdueChartData}>
              <CartesianGrid stroke={overdueChart.color("border.muted")} vertical={false} strokeDasharray="3 3" />
              <XAxis dataKey="date" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip cursor={false} animationDuration={100} content={<Chart.Tooltip />} />
              <Legend content={<Chart.Legend />} />
              {overdueChart.series.map((item) => (
                <Line key={item.name} type="monotone" isAnimationActive={false} dataKey="count" stroke={overdueChart.color(item.color)} strokeWidth={2} />
              ))}
            </LineChart>
          </Chart.Root>
        </Box>

        <Box flex={1}>
          <Text fontWeight="bold" fontSize={20} mb={4}>
            Most Borrowed Books {mostBorrowedData.length > 0 && `(${mostBorrowedData.length} books)`}
          </Text>
          {mostBorrowedData.length === 0 && !loading && (
            <Box p={4} bg="gray.50" border="1px solid" borderColor="gray.200" borderRadius="md" mb={4}>
              <Text color="gray.600" fontSize="sm">No borrowing data available. This chart uses analytics.csv data.</Text>
            </Box>
          )}
          <Chart.Root maxH="lg" chart={borrowedChart}>
            <AreaChart data={filterUser && mostBorrowedData.length > 0 ? mostBorrowedData.filter(item => item.userid === filterUser) : mostBorrowedData}>
              <CartesianGrid stroke={borrowedChart.color("border.muted")} vertical={false} strokeDasharray="3 3" />
              <XAxis dataKey="isbn" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip cursor={false} animationDuration={100} content={<Chart.Tooltip />} />
              <Legend content={<Chart.Legend />} />
              {borrowedChart.series.map((item) => (
                <defs key={item.name}>
                  <Chart.Gradient
                    id={`${item.name}-gradient`}
                    stops={[
                      { offset: "0%", color: item.color, opacity: 0.3 },
                      { offset: "100%", color: item.color, opacity: 0.05 },
                    ]}
                  />
                </defs>
              ))}
              {borrowedChart.series.map((item) => (
                <Area key={item.name} type="natural" isAnimationActive={false} dataKey="count" fill={`url(#${item.name}-gradient)`} stroke={borrowedChart.color(item.color)} strokeWidth={2} />
              ))}
            </AreaChart>
          </Chart.Root>
        </Box>
      </HStack>

      <HStack w="100%" spacing={4}>
        <Box flex={1}>
          <Text fontWeight="bold" fontSize={20} mb={4}>
            User Loan Distribution {userDistData.length > 0 && `(${userDistData.length} users)`}
          </Text>
          {userDistData.length === 0 && !loading && (
            <Box p={4} bg="gray.50" border="1px solid" borderColor="gray.200" borderRadius="md" mb={4}>
              <Text color="gray.600" fontSize="sm">No user loan distribution data available.</Text>
            </Box>
          )}
          <Chart.Root maxH="lg" chart={userChart}>
            <LineChart data={filterUser && userDistData.length > 0 ? userDistData.filter(item => item.userid === filterUser) : userDistData}>
              <CartesianGrid stroke={userChart.color("border.muted")} vertical={false} strokeDasharray="3 3" />
              <XAxis dataKey="userid" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip cursor={false} animationDuration={100} content={<Chart.Tooltip />} />
              <Legend content={<Chart.Legend />} />
              {userChart.series.map((item) => (
                <Line key={item.name} type="monotone" isAnimationActive={false} dataKey="count" stroke={userChart.color(item.color)} strokeWidth={2} />
              ))}
            </LineChart>
          </Chart.Root>
        </Box>

        <Box flex={1}>
          <Text fontWeight="bold" fontSize={20} mb={4}>
            Active Penalties by User {penaltyChartData.length > 0 && `(${penaltyChartData.length} penalties)`}
          </Text>
          {penaltyChartData.length === 0 && !loading && (
            <Box p={4} bg="gray.50" border="1px solid" borderColor="gray.200" borderRadius="md" mb={4}>
              <Text color="gray.600" fontSize="sm">No active penalties data available.</Text>
            </Box>
          )}
          <Chart.Root maxH="lg" chart={penaltyChart}>
            <BarChart data={filterUser && penaltyChartData.length > 0 ? penaltyChartData.filter(item => item.userid === filterUser) : penaltyChartData}>
              <CartesianGrid stroke={penaltyChart.color("border.muted")} vertical={false} />
              <XAxis dataKey="userid" axisLine={false} tickLine={false} />
              <YAxis axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: penaltyChart.color("bg.muted") }} animationDuration={100} content={<Chart.Tooltip />} />
              <Legend content={<Chart.Legend />} />
              {penaltyChart.series.map((item) => (
                <Bar key={item.name} isAnimationActive={false} dataKey="penalty" fill={penaltyChart.color(item.color)} />
              ))}
            </BarChart>
          </Chart.Root>
        </Box>
      </HStack>


      <Box w="100%" mt={10} p={8} bg={{base: "white", _dark: "#0f1419"}} border="1px solid" borderColor={{base: "gray.200", _dark: "#2d3748"}} borderRadius="8px">
        <Text fontWeight="bold" fontSize={20} mb={8} color={{base: "gray.900", _dark: "white"}}>
          Book Checkout Confirmation
        </Text>
        
        <HStack w="100%" spacing={20} align="flex-start">
          {/* Left Column - Confirmation Form */}
          <Box flex={1} mr={4}>
            <Text fontWeight="600" fontSize={16} mb={6} color={colors.subheaderText}>
              Process New Checkout
            </Text>
            <VStack w="100%" spacing={8} align="start">
              <Box w="100%" mb={2}>
                <Text fontWeight="500" mb={2} fontSize={13} color={colors.labelText}>User ID</Text>
                <Input
                  placeholder="Enter user ID"
                  value={checkoutUserid}
                  onChange={(e) => setCheckoutUserid(e.target.value)}
                  bg={colors.inputBg}
                  borderColor={colors.inputBorder}
                  color={colors.inputText}
                  _placeholder={{ color: colors.placeholderText }}
                  borderRadius="6px"
                  fontSize="14px"
                  p="11px 14px"
                  border="1px solid"
                  _focus={{
                    borderColor: colors.inputBorder,
                    boxShadow: "none"
                  }}
                />
              </Box>

              <Box w="100%" mb={2}>
                <Text fontWeight="500" mb={2} fontSize={13} color={colors.labelText}>ISBN</Text>
                <Input
                  placeholder="Enter book ISBN"
                  value={checkoutIsbn}
                  onChange={(e) => setCheckoutIsbn(e.target.value)}
                  bg={colors.inputBg}
                  borderColor={colors.inputBorder}
                  color={colors.inputText}
                  _placeholder={{ color: colors.placeholderText }}
                  borderRadius="6px"
                  fontSize="14px"
                  p="11px 14px"
                  border="1px solid"
                  _focus={{
                    borderColor: colors.inputBorder,
                    boxShadow: "none"
                  }}
                />
              </Box>

              <Box w="100%" mb={2}>
                <Text fontWeight="500" mb={2} fontSize={13} color={colors.labelText}>Status</Text>
                <Box
                  as="select"
                  w="100%"
                  value={checkoutStatus === "" ? "" : checkoutStatus.toString()}
                  onChange={(e) => setCheckoutStatus(e.target.value === "" ? "" : parseInt(e.target.value))}
                  bg={colors.inputBg}
                  borderColor={colors.inputBorder}
                  color={colors.inputText}
                  borderRadius="6px"
                  fontSize="14px"
                  p="11px 14px"
                  border="1px solid"
                  _focus={{
                    borderColor: colors.inputBorder,
                    boxShadow: "none"
                  }}
                  appearance="none"
                  paddingRight="32px"
                  backgroundImage={`url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23a0aec0' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e")`}
                  backgroundRepeat="no-repeat"
                  backgroundPosition="right 8px center"
                  backgroundSize="20px"
                  backgroundAttachment="scroll"
                >
                  <option value="">Select a status</option>
                  <option value="0">Not Returned</option>
                  <option value="1">Returned</option>
                  <option value="2">Returned Overdue</option>
                  <option value="3">Not Returned Overdue</option>
                  <option value="4">Cancelled</option>
                </Box>
              </Box>

              <Button
                onClick={handleConfirmCheckout}
                isDisabled={checkoutLoading}
                w="100%"
                h="40px"
                border="1px solid"
                borderColor={colors.buttonText}
                bg="transparent"
                color={colors.buttonText}
                borderRadius="6px"
                fontSize="16px"
                fontWeight="500"
                transition="all 0.2s ease"
                _hover={{
                  borderColor: colors.buttonTextHover,
                  color: colors.buttonTextHover,
                  _disabled: {
                    borderColor: colors.buttonText,
                    color: colors.buttonText,
                    opacity: 0.5
                  }
                }}
                _disabled={{
                  opacity: 0.5,
                  cursor: "not-allowed"
                }}
              >
                {checkoutLoading ? "Confirming..." : "Confirm Checkout"}
              </Button>

              {checkoutMessage && (
                <Box
                  w="100%"
                  p={3}
                  borderRadius="6px"
                  bg={checkoutMessage.includes("Error") ? "#5f1f1f" : "#1e3a2c"}
                  color={checkoutMessage.includes("Error") ? "#fca5a5" : "#86efac"}
                  fontSize={13}
                  border={`1px solid ${checkoutMessage.includes("Error") ? "#dc2626" : "#22c55e"}`}
                >
                  {checkoutMessage}
                </Box>
              )}
            </VStack>
          </Box>

          {/* Right Column - Pending Checkouts */}
          <Box flex={1}>
            <Text fontWeight="600" fontSize={16} mb={6} color={colors.subheaderText}>
              Pending Checkouts ({pendingCheckouts.length})
            </Text>
            <VStack w="100%" spacing={3} align="stretch" maxH="380px" overflowY="auto" pr={2}>
              {pendingCheckouts.length > 0 ? (
                pendingCheckouts.map((checkout, idx) => (
                  <Box
                    key={idx}
                    p={4}
                    border="1px solid"
                    borderColor={colors.inputBorder}
                    borderRadius="6px"
                    bg={colors.inputBg}
                    _hover={{ bg: { base: "gray.100", _dark: "#374151" }, cursor: "pointer" }}
                    onClick={() => {
                      setCheckoutUserid(checkout.userid);
                      setCheckoutIsbn(checkout.isbn);
                    }}
                  >
                    <HStack w="100%" justify="space-between" mb={2}>
                      <Text fontWeight="600" fontSize={13} color={colors.inputText}>{checkout.userid}</Text>
                      <Text fontSize={11} color={colors.labelText}>{checkout.timestamp}</Text>
                    </HStack>
                    <Text fontSize={12} color={colors.labelText}>{checkout.title}</Text>
                    <Text fontSize={11} color={colors.placeholderText} mt={2}>ISBN: {checkout.isbn}</Text>
                  </Box>
                ))
              ) : (
                <Text color={colors.labelText} fontSize={13}>No pending checkouts</Text>
              )}
            </VStack>
          </Box>
        </HStack>

        {/* Bottom Section - Confirmed Checkouts History */}
        <Box mt={10} pt={8} borderTop="1px solid" borderTopColor={colors.inputBorder}>
          <Text fontWeight="600" fontSize={16} mb={6} color={colors.subheaderText}>
            Recent Confirmations ({confirmedCheckouts.length})
          </Text>
          <VStack w="100%" spacing={3} align="stretch" maxH="320px" overflowY="auto">
            {confirmedCheckouts.map((checkout, idx) => {
              const bgColor = checkout.status === "Returned" 
                ? { base: "#dcf5e3", _dark: "#1e3a2c" }
                : checkout.status === "Returned Overdue" 
                ? { base: "#ffeaa7", _dark: "#3f3018" }
                : { base: "#ffd3d3", _dark: "#3a1f1f" };
              
              const textColor = checkout.status === "Returned" 
                ? { base: "#22c55e", _dark: "#86efac" }
                : checkout.status === "Returned Overdue" 
                ? { base: "#f59e0b", _dark: "#fbbf24" }
                : { base: "#dc2626", _dark: "#fca5a5" };
              
              const borderColor = checkout.status === "Returned" 
                ? { base: "#86efac", _dark: "#22c55e" }
                : checkout.status === "Returned Overdue" 
                ? { base: "#fbbf24", _dark: "#f59e0b" }
                : { base: "#fca5a5", _dark: "#dc2626" };
              
              return (
                <Box
                  key={idx}
                  p={4}
                  border="1px solid"
                  borderColor={colors.inputBorder}
                  borderRadius="6px"
                  bg={bgColor}
                >
                  <HStack w="100%" justify="space-between">
                    <Box flex={1}>
                      <Text fontWeight="600" fontSize={13} color={colors.inputText}>{checkout.userid}</Text>
                      <Text fontSize={12} color={colors.labelText}>{checkout.title}</Text>
                      <Text fontSize={11} color={colors.placeholderText} mt={2}>ISBN: {checkout.isbn}</Text>
                    </Box>
                    <Box textAlign="right">
                      <Text
                        fontSize={11}
                        fontWeight="600"
                        color={textColor}
                        px={3}
                        py={1}
                        borderRadius="4px"
                        border="1px solid"
                        borderColor={borderColor}
                        mb={2}
                      >
                        {checkout.status}
                      </Text>
                      <Text fontSize={11} color={colors.placeholderText}>{checkout.timestamp}</Text>
                    </Box>
                  </HStack>
                </Box>
              );
            })}
          </VStack>
        </Box>
      </Box>

      <Button
        w="100%"
        h="44px" 
        bg={{ base: "black", _dark: "white" }}
        color={{ base: "white", _dark: "gray.900" }}
        fontWeight="600"
        fontSize="md"
        borderRadius="6px"
        mt={10}
        onClick={() => router.push('/penaltymanagement')}
        _hover={{ bg: { base: "gray.800", _dark: "gray.100" } }}
      >
        Penalty Management
      </Button>
    </VStack>
  )
};

export default adminpage;