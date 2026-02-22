import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, Eye, EyeOff, ArrowRight, ArrowLeft, Globe } from 'lucide-react';
import { apiService } from '../../services/api';
import toast from 'react-hot-toast';

const ResetPassword = () => {
    const [formData, setFormData] = useState({
        password: '',
        confirmPassword: ''
    });
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);

    const navigate = useNavigate();
    const location = useLocation();

    const token = new URLSearchParams(location.search).get('token');

    useEffect(() => {
        if (!token) {
            toast.error('Invalid or missing reset token.');
            navigate('/login');
        }
    }, [token, navigate]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (formData.password !== formData.confirmPassword) {
            toast.error('Passwords do not match');
            return;
        }

        if (formData.password.length < 6) {
            toast.error('Password must be at least 6 characters');
            return;
        }

        setIsLoading(true);
        try {
            await apiService.resetPassword(token, formData.password);
            setIsSuccess(true);
            toast.success('Password reset successfully!');
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Failed to reset password. Token may be expired.');
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
                        <h2 className="text-3xl font-bold text-white mb-2">Choose New Password</h2>
                        <p className="text-gray-300">
                            {isSuccess ? 'Password updated' : 'Please enter your new password'}
                        </p>
                    </div>

                    {!isSuccess ? (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            {/* password */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    New Password
                                </label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type={showPassword ? 'text' : 'password'}
                                        name="password"
                                        value={formData.password}
                                        onChange={handleChange}
                                        required
                                        className="input-futuristic w-full pl-10 pr-12 py-3 rounded-lg border focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                                        placeholder="Enter new password"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                                    >
                                        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                            </div>

                            {/* Confirm password */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Confirm New Password
                                </label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                    <input
                                        type={showConfirmPassword ? 'text' : 'password'}
                                        name="confirmPassword"
                                        value={formData.confirmPassword}
                                        onChange={handleChange}
                                        required
                                        className="input-futuristic w-full pl-10 pr-12 py-3 rounded-lg border focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                                        placeholder="Confirm new password"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                                    >
                                        {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                    </button>
                                </div>
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="w-full btn-gradient py-3 rounded-lg font-semibold text-white flex items-center justify-center gap-2 hover:shadow-glow transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isLoading ? (
                                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                ) : (
                                    <>
                                        Reset Password
                                        <ArrowRight className="w-5 h-5" />
                                    </>
                                )}
                            </button>
                        </form>
                    ) : (
                        <div className="text-center space-y-6">
                            <div className="p-4 bg-green-500/10 rounded-lg border border-green-500/20 text-green-400">
                                Your password has been successfully reset. You can now log in with your new password.
                            </div>

                            <Link
                                to="/login"
                                className="w-full btn-gradient py-3 rounded-lg font-semibold text-white flex items-center justify-center gap-2 hover:shadow-glow transition-all"
                            >
                                Go to Login
                                <ArrowRight className="w-5 h-5" />
                            </Link>
                        </div>
                    )}

                    {/* Links */}
                    {!isSuccess && (
                        <div className="mt-8 text-center pt-6 border-t border-white/10">
                            <Link
                                to="/login"
                                className="inline-flex items-center justify-center gap-2 text-primary-400 hover:text-primary-300 font-medium transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Back to Login
                            </Link>
                        </div>
                    )}
                </motion.div>
            </div>
        </div>
    );
};

export default ResetPassword;
