"use client";
import React from "react";

export default function BorrowedPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 font-sans text-gray-800 p-8">
      <h1 className="text-3xl font-bold mb-4 flex items-center text-blue-900">
        🔁 Borrowed Books
      </h1>

      <p className="text-gray-700 mb-6">
        Track books you have borrowed and their due dates.
      </p>

      <div className="bg-white rounded-xl shadow-md p-6 overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b">
              <th className="p-3 font-semibold text-gray-900">Title</th>
              <th className="p-3 font-semibold text-gray-900">Author</th>
              <th className="p-3 font-semibold text-gray-900">Due Date</th>
              <th className="p-3 font-semibold text-gray-900">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b hover:bg-gray-50 transition">
              <td className="p-3">The Pragmatic Programmer</td>
              <td className="p-3">Andrew Hunt</td>
              <td className="p-3">Nov 20, 2025</td>
              <td className="p-3 text-green-600 font-medium">On Time</td>
            </tr>
            <tr className="border-b hover:bg-gray-50 transition">
              <td className="p-3">Clean Code</td>
              <td className="p-3">Robert C. Martin</td>
              <td className="p-3">Nov 5, 2025</td>
              <td className="p-3 text-red-600 font-medium">Overdue</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
