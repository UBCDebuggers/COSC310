import Link from "next/link";
import Image from "next/image";
import { Home, Book, Star, Repeat, User, Settings } from "lucide-react";

export default function Menu() {
  // Organized menu structure
  const menuItems = [
    {
      title: "MENU",
      items: [
        { label: "Home", href: "/login", icon: <Home size={18} /> },
        { label: "Browse Books", href: "/books", icon: <Book size={18} /> },
        { label: "My Watchlist", href: "/watchlist", icon: <Star size={18} /> },
        { label: "Borrowed Books", href: "/borrowed", icon: <Repeat size={18} /> },
      ],
    },
    {
      title: "OTHER",
      items: [
        { label: "Profile", href: "/profile", icon: <User size={18} /> },
        { label: "Settings", href: "/settings", icon: <Settings size={18} /> },
      ],
    },
  ];

  return (
    <div className="flex flex-col h-full text-gray-900 px-6 py-8">
      {/* Header */}
      <div className="flex flex-col items-center mb-4">
      </div>

      {/* Dynamic Menu Mapping */}
      {menuItems.map((section, index) => (
        <div key={section.title}>
          {/* Divider before each section (except first) */}
          {index !== 0 && <div className="border-t border-gray-400 my-4" />}

          {/* Section Title */}
          <span className="hidden lg:block text-gray-700 text-sm font-bold tracking-widest mb-3">
            {section.title}
          </span>

          {/* Items */}
          <div className="flex flex-col gap-3">
            {section.items.map((item) => (
              <Link
                href={item.href}
                key={item.label}
                className="flex items-center gap-3 text-gray-800 hover:text-pink-700 transition"
              >
                {item.icon}
                <span className="hidden lg:block">{item.label}</span>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
