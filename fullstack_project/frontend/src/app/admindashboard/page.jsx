"use client";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Box, Text, VStack, HStack, Button, FileUpload, Center } from "@chakra-ui/react";
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
  const [useUploadedData, setUseUploadedData] = useState(false);
  const [uploadedLoans, setUploadedLoans] = useState([]);
  const [uploadedPenalties, setUploadedPenalties] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [filterUser, setFilterUser] = useState("");
  const [loansUploadedFile, setLoansUploadedFile] = useState(null);
  const [loansUploadedData, setLoansUploadedData] = useState([]);

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
            isAdmin = payload.admin || false;
          } catch (e) {
            // Token decode failed, continue without user info
          }
        }

        const [items, popularItems, engagingItems, userItems, outstandingItems, penaltyItems] = await Promise.all([
          fetch("http://localhost:8000/recommend/toprated/5").then((r) => r.json()).catch(() => []),
          fetch("http://localhost:8000/recommend/popular/10").then((r) => r.json()).catch(() => []),
          fetch("http://localhost:8000/recommend/topengagement/10").then((r) => r.json()).catch(() => []),
          isAdmin ? fetch("http://localhost:8000/library/userloans?userid=" + encodeURIComponent(userInfo?.sub || ""), { headers }).then((r) => r.ok ? r.json() : []).catch(() => []) : Promise.resolve([]),
          isAdmin ? fetch("http://localhost:8000/library/outstandingloans", { headers }).then((r) => r.ok ? r.json() : []).catch(() => []) : Promise.resolve([]),
          isAdmin ? fetch("http://localhost:8000/library/activepenalties", { headers }).then((r) => r.ok ? r.json() : []).catch(() => []) : Promise.resolve([]),
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

        // Only update chart data if API returned actual data
        if (outstandingItems && outstandingItems.length > 0) {
          setLoansChartData(transformLoansByDate(outstandingItems));
          setOverdueChartData(transformOverdueTrend(outstandingItems));
          setMostBorrowedData(transformMostBorrowed(outstandingItems));
        }
        if (userItems && userItems.length > 0) {
          setUserDistData(transformUserDistribution(userItems));
        }
        if (penaltyItems && penaltyItems.length > 0) {
          setPenaltyChartData(transformPenaltiesByUser(penaltyItems));
        }

        setLoading(false);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError(error.message);
        setLoading(false);
      }
    };

    // Set demo data as initial state
    setLoansChartData([
      { date: "12/25/2024", count: 2, userid: "user3" },
      { date: "12/28/2024", count: 1, userid: "user2" },
      { date: "12/30/2024", count: 1, userid: "user3" },
      { date: "01/15/2025", count: 2, userid: "user1" },
      { date: "01/20/2025", count: 1, userid: "user2" },
      { date: "02/05/2025", count: 1, userid: "user4" },
      { date: "02/10/2025", count: 1, userid: "user1" },
    ]);
    setOverdueChartData([
      { date: "12/25/2024", count: 1, userid: "user3" },
      { date: "12/28/2024", count: 1, userid: "user2" },
      { date: "12/30/2024", count: 1, userid: "user3" },
    ]);
    setMostBorrowedData([
      { isbn: "978-0-123456", count: 5, userid: "user1" },
      { isbn: "978-0-789012", count: 4, userid: "user1" },
      { isbn: "978-0-345678", count: 3, userid: "user2" },
      { isbn: "978-0-456789", count: 3, userid: "user3" },
      { isbn: "978-0-567890", count: 2, userid: "user4" },
      { isbn: "978-0-654321", count: 2, userid: "user2" },
      { isbn: "978-0-987654", count: 2, userid: "user1" },
    ]);
    setUserDistData([
      { userid: "user1", count: 3 },
      { userid: "user2", count: 2 },
      { userid: "user3", count: 2 },
      { userid: "user4", count: 1 },
    ]);
    setPenaltyChartData([
      { userid: "user1", penalty: 28.00 },
      { userid: "user2", penalty: 15.50 },
      { userid: "user3", penalty: 42.75 },
      { userid: "user4", penalty: 8.25 },
    ]);

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

  const getLoansChartData = () => {
    if (loansUploadedData.length > 0) {
      return loansUploadedData;
    }
    return getFilteredData().loans;
  };

  const loansChart = useChart({
    data: getLoansChartData().length > 0 ? getLoansChartData() : [
      { date: "12/25/2024", count: 2 },
      { date: "12/28/2024", count: 1 },
      { date: "12/30/2024", count: 1 },
      { date: "01/15/2025", count: 2 },
      { date: "01/20/2025", count: 1 },
      { date: "02/05/2025", count: 1 },
      { date: "02/10/2025", count: 1 },
    ],
    series: [{ name: "count", color: "blue.solid" }],
  });

  const overdueChart = useChart({
    data: getFilteredData().overdue.length > 0 ? getFilteredData().overdue : [
      { date: "12/25/2024", count: 1, userid: "user3" },
      { date: "12/28/2024", count: 1, userid: "user2" },
      { date: "12/30/2024", count: 1, userid: "user3" },
    ],
    series: [{ name: "count", color: "red.solid" }],
  });

  const borrowedChart = useChart({
    data: filterUser && mostBorrowedData.length > 0
      ? mostBorrowedData.filter(item => item.userid === filterUser)
      : (mostBorrowedData.length > 0 ? mostBorrowedData : [
          { isbn: "978-0-123456", count: 5, userid: "user1" },
          { isbn: "978-0-789012", count: 4, userid: "user1" },
          { isbn: "978-0-345678", count: 3, userid: "user2" },
          { isbn: "978-0-456789", count: 3, userid: "user3" },
          { isbn: "978-0-567890", count: 2, userid: "user4" },
        ]),
    series: [{ name: "count", color: "green.solid" }],
  });

  const userChart = useChart({
    data: filterUser && userDistData.length > 0 
      ? userDistData.filter(item => item.userid === filterUser)
      : (userDistData.length > 0 ? userDistData : [
          { userid: "user1", count: 3 },
          { userid: "user2", count: 2 },
          { userid: "user3", count: 2 },
          { userid: "user4", count: 1 },
        ]),
    series: [{ name: "count", color: "purple.solid" }],
  });

  const penaltyChart = useChart({
    data: filterUser && penaltyChartData.length > 0 
      ? penaltyChartData.filter(item => item.userid === filterUser)
      : (penaltyChartData.length > 0 ? penaltyChartData : [
          { userid: "user1", penalty: 28.00 },
          { userid: "user2", penalty: 15.50 },
          { userid: "user3", penalty: 42.75 },
          { userid: "user4", penalty: 8.25 },
        ]),
    series: [{ name: "penalty", color: "orange.solid" }],
  });

  const chart = useChart({
    data: [
      { windows: 186, mac: 80, linux: 120, month: "January" },
      { windows: 165, mac: 95, linux: 110, month: "February" },
      { windows: 190, mac: 87, linux: 125, month: "March" },
      { windows: 195, mac: 88, linux: 130, month: "May" },
      { windows: 182, mac: 98, linux: 122, month: "June" },
      { windows: 175, mac: 90, linux: 115, month: "August" },
      { windows: 180, mac: 86, linux: 124, month: "October" },
      { windows: 185, mac: 91, linux: 126, month: "November" },
    ],
    series: [
      { name: "windows", color: "teal.solid" },
      { name: "mac", color: "purple.solid" },
      { name: "linux", color: "blue.solid" },
    ],
  });

  return (
    <VStack w="100%" spacing={8} p={10}>
      <VStack w="100%" align="start" spacing={4} pb={6} borderBottom="1px" borderColor="gray.200">
        <Text fontWeight="bold" fontSize={28}>
          Admin Dashboard
        </Text>
        <HStack w="100%">
          <input type="text" placeholder="Filter by User ID (e.g., user1)" value={filterUser} onChange={(e) => setFilterUser(e.target.value)} style={{ padding: "8px 12px", border: "1px solid #ccc", borderRadius: "4px", minWidth: "250px" }} />
          {filterUser && <Button size="sm" onClick={() => setFilterUser("")}>Clear</Button>}
        </HStack>
      </VStack>

      <Chart.Root maxH="sm" chart={chart}>
      <AreaChart data={chart.data}>
        <CartesianGrid
          stroke={chart.color("border")}
          vertical={false}
          strokeDasharray="3 3"
        />
        <XAxis
          dataKey={chart.key("month")}
          tickLine={false}
          axisLine={false}
          tickMargin={8}
          tickFormatter={(value) => value.slice(0, 3)}
        />
        <YAxis tickLine={false} axisLine={false} />
        <Tooltip
          cursor={false}
          animationDuration={100}
          content={<Chart.Tooltip />}
        />
        <Legend content={<Chart.Legend />} />

        {chart.series.map((item) => (
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

        {chart.series.map((item) => (
          <Area
            key={item.name}
            type="natural"
            isAnimationActive={false}
            dataKey={chart.key(item.name)}
            fill={`url(#${item.name}-gradient)`}
            stroke={chart.color(item.color)}
            strokeWidth={2}
            stackId="a"
          />
        ))}
      </AreaChart>
    </Chart.Root>

      <Box w="100%">
        <Text fontWeight="bold" fontSize={20} mb={4}>
          Loans by Expiry Date
        </Text>
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

      <HStack w="100%" spacing={8}>
        <Box flex={1}>
          <Text fontWeight="bold" fontSize={20} mb={4}>
            Overdue Loans Trend
          </Text>
          <Chart.Root maxH="md" chart={overdueChart}>
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
            Most Borrowed Books
          </Text>
          <Chart.Root maxH="md" chart={borrowedChart}>
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

      <HStack w="100%" spacing={8}>
        <Box flex={1}>
          <Text fontWeight="bold" fontSize={20} mb={4}>
            User Loan Distribution
          </Text>
          <Chart.Root maxH="md" chart={userChart}>
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
            Active Penalties by User
          </Text>
          <Chart.Root maxH="md" chart={penaltyChart}>
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
    </VStack>
  )
};

export default adminpage;