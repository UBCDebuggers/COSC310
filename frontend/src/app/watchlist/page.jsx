"use client";

import React from "react";

export default function WatchlistPage() {
  return (
    <div className="p-8 min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 font-sans">
     <h1 className="text-3xl font-bold mb-4 text-red-800 flex items-center ">
      <span className="mr-2 text-yellow-500 text-4xl">⭐</span>
      My Watchlist
    </h1>


      <p className="text-gray-700 mb-6">
        Here are the books you’ve added to your personal watchlist.
      </p>

      <ul className="space-y-3">
        <li className="border border-gray-200 p-4 rounded-xl shadow-sm hover:bg-white hover:shadow-md transition-all duration-200">
          <span className="font-semibold text-gray-900">Atomic Habits</span> —{" "}
          <span className="text-gray-600">James Clear</span>
        </li>

        <li className="border border-gray-200 p-4 rounded-xl shadow-sm hover:bg-white hover:shadow-md transition-all duration-200">
          <span className="font-semibold text-gray-900">Deep Work</span> —{" "}
          <span className="text-gray-600">Cal Newport</span>
        </li>
      </ul>
    </div>
  );
}
