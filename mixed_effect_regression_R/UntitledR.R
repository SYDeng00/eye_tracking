library(lme4)
library(readxl)
library(ggplot2)
# 替换文件路径为你的Excel文件路径
file_path <- "D:/DTU document/1st/cognitive experiment/(new)mixed_logistic_regression.xlsx"
data <- read_excel(file_path)
model <- glmer(brand_recall ~ consistency + celebrity_familiarity + brand_familiarity + (1 | test_ID), 
               data = data, 
               family = binomial)
summary(model)

reduced_model <- glm(brand_recall ~ consistency + brand_familiarity + celebrity_familiarity, 
                     data = data, 
                     family = binomial)
summary(reduced_model)
# 使用anova函数进行似然比检验
lrt_result <- anova(reduced_model, model, test="Chisq")
print(lrt_result)

#---------------------------------coefficient plot-----------------------------------------------------

# 提取固定效应的系数
model_coef <- fixef(model)

# 提取置信区间
model_confint <- confint(model)

# 选择与固定效应系数对应的置信区间
model_confint <- model_confint[names(model_coef), ]

coef_df <- data.frame(Estimate = model_coef,
                      Lower = model_confint[, 1],
                      Upper = model_confint[, 2])

# 绘制系数图
ggplot(coef_df, aes(y = names(model_coef), x = Estimate)) +
  geom_point() +
  geom_errorbarh(aes(xmin = Lower, xmax = Upper)) +
  theme_minimal() +
  xlab("Estimate") +
  ylab("Variable")

#--------------------------------------predict probablity------------------------------
# 创建预测数据集
newdata <- expand.grid(consistency = c(0, 1),
                       celebrity_familiarity = seq(min(data$celebrity_familiarity), max(data$celebrity_familiarity), length.out = 5),
                       brand_familiarity = seq(min(data$brand_familiarity), max(data$brand_familiarity), length.out = 3))

# 添加随机效应的平均值
newdata$test_ID <- factor(1)  # 假设test_ID为随机效应
# 预测brand_recall的概率
newdata$predicted_prob <- predict(model, newdata = newdata, type = "response", re.form = NA)
# 使用ggplot绘制图表
ggplot(newdata, aes(x = celebrity_familiarity, y = predicted_prob, color = factor(consistency))) +
  geom_line() +
  facet_wrap(~ brand_familiarity) + # 使用brand_familiarity作为面板变量
  theme_minimal() +
  labs(color = "Consistency", x = "Celebrity Familiarity", y = "Predicted Brand Recall Probability")

#--------------------------------------ROC--------------------------------------------------------------
library(pROC)

# 使用模型预测
predictions <- predict(model, type = "response")

# 真实值
actuals <- data$brand_recall

roc_curve <- roc(actuals, predictions)

# 计算AUC
auc_value <- auc(roc_curve)
print(auc_value)
# 绘制ROC曲线并添加AUC
plot(roc_curve)
text(0.6, 0.5, paste("AUC =", round(auc_value, 2)))