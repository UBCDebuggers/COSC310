"use client";
import React from "react";

export default function ProfilePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 font-sans text-gray-800 p-8">
      <h1 className="text-3xl font-bold mb-4 flex items-center text-blue-900">
        👤 Profile
      </h1>

      <p className="text-gray-700 mb-6">
        View and manage your personal details and library activity.
      </p>

      <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-6 max-w-md transition hover:shadow-xl">
        <h2 className="font-semibold text-xl mb-4 text-gray-900">
          User Information
        </h2>

        <div className="space-y-2 text-gray-700">
          <p>
            <strong className="text-gray-900">Name:</strong> Ahab Masud Siddiqui
          </p>
          <p>
            <strong className="text-gray-900">Email:</strong> ahab@library.ca
          </p>
          <p>
            <strong className="text-gray-900">Member Since:</strong> January 2024
          </p>
          <p>
            <strong className="text-gray-900">Borrowed Books:</strong> 5
          </p>
        </div>
      </div>
    </div>
  );
}
