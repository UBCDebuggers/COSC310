import React from "react";
import Link from "next/link";
import Image from "next/image";
import Menu from "@/components/Menu";
import Navbar from "@/components/Navbar";

export default function DashboardLayout({
  children,
}) {
  return (
    <div className="h-screen flex">
      {/* LEFT */}
      <div className="w-[14%] md:w-[8%] lg:w-[16%] xl:w-[14%]  bg-[#F7F8FA] p-4">
        <Link 
        href="/login" 
        className="flex items-center justify-center lg:justify-start gap-2 text-black no-underline hover:text-red-500">
        <Image src = "/favicon.ico" alt = "Logo" width ={40} height ={40} />
        <span className="hidden lg:block" >Library System </span>
        </Link>
        <Menu/>
      </div>
      {/* RIGHT */}
      <div className="w-[86%] md:w-[92%] lg:w-[84%] xl:w-[86%] bg-[#F7F8FA] overflow - scroll "> <Navbar />{children}</div>
    </div>
  );
}
