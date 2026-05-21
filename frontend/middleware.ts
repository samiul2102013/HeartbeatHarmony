import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const token = request.cookies.get("heartbeat_harmony_admin_access")?.value;

  // Public auth routes that don't need authentication
  const publicAuthRoutes = ["/signin", "/forgot-password", "/verification", "/reset-password"];
  const isPublicAuthRoute = publicAuthRoutes.some((route) => pathname.startsWith(route));

  // Protected dashboard routes that need authentication
  const protectedRoutes = ["/", "/users", "/check-ins", "/categories", "/mood-categories", "/mood-scoring", "/study-scoring", "/study-materials", "/subject-uploads", "/quiz-test", "/pricing", "/settings"];
  const isProtectedRoute = protectedRoutes.some((route) => pathname === route || pathname.startsWith(route + "/"));

  // If user is not authenticated
  if (!token) {
    // Redirect to signin if trying to access protected routes
    if (isProtectedRoute) {
      return NextResponse.redirect(new URL("/signin", request.url));
    }
    // Allow access to public auth routes
    return NextResponse.next();
  }

  // If user is authenticated
  if (token) {
    // Redirect away from auth pages to dashboard
    if (isPublicAuthRoute && pathname !== "/signin") {
      return NextResponse.redirect(new URL("/", request.url));
    }
    // Allow access to protected routes and signin
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|public).*)",
  ],
};
