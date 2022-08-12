USE Монеты
GO
CREATE PROC Фильтр_категорий
@year_before integer, @year_after integer, @price_before integer, @price_after integer, @country nvarchar(30), @nominal nvarchar(30)
AS BEGIN
SELECT ИДМонеты, Название, Страна, Год, Тираж, Материал, Диаметр, Цена, Фото
FROM Монеты
WHERE (@year_before<=Год OR @year_before IS NULL) AND (@year_after>=Год OR @year_after IS NULL) AND (@price_before<=Цена OR @price_before IS NULL) AND (@price_after>=Цена OR @price_after IS NULL) AND (@country=Страна OR @country IS NULL) AND (@nominal=Название OR @nominal IS NULL)
END
