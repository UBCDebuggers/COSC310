"use client";
import React, { useState } from "react";

export default function SettingsPage() {
  const [notifications, setNotifications] = useState(true);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 font-sans text-gray-800 p-8">
      <h1 className="text-3xl font-bold mb-4 flex items-center text-blue-900">
        ⚙️ Settings
      </h1>

      <p className="text-gray-700 mb-6">
        Customize your library experience and preferences.
      </p>

      <div className="bg-white border border-gray-200 rounded-2xl shadow-lg p-6 max-w-md transition hover:shadow-xl">
        <h2 className="font-semibold text-xl mb-4 text-gray-900">
          Preferences
        </h2>

        <div className="flex items-center justify-between mb-6">
          <span className="text-gray-800 font-medium">
            Enable Email Notifications
          </span>
          <input
            type="checkbox"
            checked={notifications}
            onChange={() => setNotifications(!notifications)}
            className="w-5 h-5 accent-blue-600 cursor-pointer"
          />
        </div>

        <button
          onClick={() => alert("Settings saved successfully!")}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 transition"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
}
