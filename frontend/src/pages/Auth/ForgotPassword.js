import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, ArrowLeft, ArrowRight, Globe } from 'lucide-react';
import { apiService } from '../../services/api';
import toast from 'react-hot-toast';

const ForgotPassword = () => {
    const location = useLocation();
    const [email, setEmail] = useState(location.state?.email || '');
    const [isLoading, setIsLoading] = useState(false);
    const [isSent, setIsSent] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!email) return;

        setIsLoading(true);
        try {
            await apiService.forgotPassword(email);
            setIsSent(true);
            toast.success('If an account exists, a password reset link will be sent.');
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Failed to send reset link.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-20">
            <div className="max-w-md w-full">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                    className="glass rounded-2xl p-8 shadow-2xl"
                >
                    {/* Logo */}
                    <div className="text-center mb-8">
                        <div className="flex items-center justify-center mb-4">
                            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
                                <Globe className="w-6 h-6 text-white" />
                            </div>
                        </div>
                        <h2 className="text-3xl font-bold text-white mb-2">Reset Password</h2>
                        <p className="text-gray-300">
                            {isSent ? 'Check your email inbox' : 'Enter your email to receive a reset link'}
                        </p>
                    </div>

                    {!isSent ? (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Email
                                </label>
                                <div className="relative">
                                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        className="input-futuristic w-full pl-10 pr-4 py-3 rounded-lg border focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                                        placeholder="Enter your email"
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full btn-gradient py-3 rounded-lg font-semibold text-white flex items-center justify-center gap-2 hover:shadow-glow transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isLoading ? (
                                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                ) : (
                                    <>
                                        Send Reset Link
                                        <ArrowRight className="w-5 h-5" />
                                    </>
                                )}
                            </button>
                        </form>
                    ) : (
                        <div className="text-center">
                            <div className="p-4 bg-primary-500/10 rounded-lg border border-primary-500/20 text-gray-300 mb-6">
                                We've sent a password reset link to <span className="text-white font-medium">{email}</span>.
                                Please check your inbox and spam folder.
                            </div>
                        </div>
                    )}

                    {/* Links */}
                    <div className="mt-8 text-center pt-6 border-t border-white/10">
                        <Link
                            to="/login"
                            className="inline-flex items-center justify-center gap-2 text-primary-400 hover:text-primary-300 font-medium transition-colors"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            Back to Login
                        </Link>
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default ForgotPassword;
