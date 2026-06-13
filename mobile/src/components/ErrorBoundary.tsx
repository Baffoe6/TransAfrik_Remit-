import React, { Component, type ErrorInfo, type ReactNode } from "react";
import { View, Text, TouchableOpacity } from "react-native";
import { lightTheme } from "../theme/colors";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("App error:", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 24, backgroundColor: lightTheme.bg }}>
            <Text style={{ fontSize: 22, fontWeight: "700", color: lightTheme.primary, marginBottom: 8 }}>Something went wrong</Text>
            <Text style={{ color: lightTheme.textSecondary, textAlign: "center", marginBottom: 24 }}>
              Please restart the app. If the problem continues, contact support.
            </Text>
            <TouchableOpacity
              onPress={() => this.setState({ hasError: false })}
              style={{ backgroundColor: lightTheme.primary, paddingHorizontal: 24, paddingVertical: 14, borderRadius: 12 }}
            >
              <Text style={{ color: "#fff", fontWeight: "600" }}>Try Again</Text>
            </TouchableOpacity>
          </View>
        )
      );
    }
    return this.props.children;
  }
}
